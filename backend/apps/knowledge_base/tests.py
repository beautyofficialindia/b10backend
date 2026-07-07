from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.knowledge_base.models import KnowledgeEntry
from apps.knowledge_base.serializers import (
    KnowledgeEntryDetailSerializer,
    KnowledgeEntryListSerializer,
    KnowledgeEntryWriteSerializer,
)
from apps.knowledge_base.services.knowledge_service import KnowledgeService

User = get_user_model()


class KnowledgeEntryModelTests(TestCase):
    """Tests for KnowledgeEntry model behavior."""

    def test_auto_slug_generation(self):
        entry = KnowledgeEntry.objects.create(
            category='faq', title='How to Reset Password', content='Go to settings.'
        )
        self.assertEqual(entry.slug, 'how-to-reset-password')

    def test_slug_collision_appends_uuid_suffix(self):
        KnowledgeEntry.objects.create(
            category='faq', title='Test Entry', content='First'
        )
        entry2 = KnowledgeEntry.objects.create(
            category='faq', title='Test Entry', content='Second'
        )
        self.assertTrue(entry2.slug.startswith('test-entry-'))
        self.assertNotEqual(entry2.slug, 'test-entry')
        self.assertEqual(len(entry2.slug), len('test-entry-') + 8)

    def test_published_at_auto_stamped_on_first_publish(self):
        entry = KnowledgeEntry.objects.create(
            category='faq', title='Pub Test', content='x'
        )
        self.assertIsNone(entry.published_at)
        entry.status = 'published'
        entry.save()
        entry.refresh_from_db()
        self.assertIsNotNone(entry.published_at)

    def test_published_at_not_overwritten_on_re_publish(self):
        entry = KnowledgeEntry.objects.create(
            category='faq', title='Re-Pub Test', content='x', status='published'
        )
        first_published_at = entry.published_at
        entry.status = 'draft'
        entry.save()
        entry.status = 'published'
        entry.save()
        entry.refresh_from_db()
        self.assertEqual(entry.published_at, first_published_at)

    def test_deleted_at_auto_stamped_on_soft_delete(self):
        entry = KnowledgeEntry.objects.create(
            category='faq', title='Del Test', content='x'
        )
        self.assertIsNone(entry.deleted_at)
        entry.is_deleted = True
        entry.save()
        entry.refresh_from_db()
        self.assertIsNotNone(entry.deleted_at)

    def test_str_format(self):
        entry = KnowledgeEntry(category='service', title='Web Development')
        self.assertEqual(str(entry), '[service] Web Development')

    def test_meta_ordering(self):
        self.assertEqual(
            KnowledgeEntry._meta.ordering,
            ['category', 'sort_order', 'created_at'],
        )


class KnowledgeServiceTests(TestCase):
    """Tests for KnowledgeService."""

    def setUp(self):
        self.user = User.objects.create_user(username='admin', password='pass')
        self.entry1 = KnowledgeEntry.objects.create(
            category='faq', title='FAQ 1', content='Answer 1', status='published'
        )
        self.entry2 = KnowledgeEntry.objects.create(
            category='service', title='Web Dev', content='We build web apps', status='draft'
        )
        self.entry3 = KnowledgeEntry.objects.create(
            category='faq', title='FAQ 2', content='Answer 2', status='published', is_deleted=True
        )

    def test_list_entries_no_filter(self):
        entries = KnowledgeService.list_entries()
        # Excludes soft-deleted by default
        self.assertEqual(entries.count(), 2)

    def test_list_entries_category_filter(self):
        entries = KnowledgeService.list_entries(category='faq')
        self.assertEqual(entries.count(), 1)
        self.assertEqual(entries.first().pk, self.entry1.pk)

    def test_list_entries_search_filter(self):
        entries = KnowledgeService.list_entries(search='web')
        self.assertEqual(entries.count(), 1)
        self.assertEqual(entries.first().pk, self.entry2.pk)

    def test_list_entries_search_whitespace_ignored(self):
        entries = KnowledgeService.list_entries(search='   ')
        self.assertEqual(entries.count(), 2)

    def test_list_entries_status_filter(self):
        entries = KnowledgeService.list_entries(status='published')
        self.assertEqual(entries.count(), 1)
        self.assertEqual(entries.first().pk, self.entry1.pk)

    def test_list_entries_include_deleted(self):
        entries = KnowledgeService.list_entries(include_deleted=True)
        self.assertEqual(entries.count(), 3)

    def test_get_entry(self):
        entry = KnowledgeService.get_entry(self.entry1.pk)
        self.assertEqual(entry.pk, self.entry1.pk)

    def test_get_entry_not_found(self):
        import uuid
        with self.assertRaises(KnowledgeEntry.DoesNotExist):
            KnowledgeService.get_entry(uuid.uuid4())

    def test_get_entry_excludes_deleted(self):
        with self.assertRaises(KnowledgeEntry.DoesNotExist):
            KnowledgeService.get_entry(self.entry3.pk)

    def test_create_entry_valid(self):
        entry = KnowledgeService.create_entry(
            data={'category': 'faq', 'title': 'New FAQ', 'content': 'Answer'},
            user=self.user,
        )
        self.assertEqual(entry.status, 'draft')
        self.assertEqual(entry.source, 'manual')
        self.assertEqual(entry.created_by, self.user)
        self.assertTrue(entry.slug)

    def test_create_entry_missing_category(self):
        with self.assertRaises(ValueError) as ctx:
            KnowledgeService.create_entry(data={'title': 'No Cat'}, user=self.user)
        self.assertIn('category', str(ctx.exception))

    def test_create_entry_missing_title(self):
        with self.assertRaises(ValueError) as ctx:
            KnowledgeService.create_entry(data={'category': 'faq'}, user=self.user)
        self.assertIn('title', str(ctx.exception))

    def test_update_entry_valid(self):
        entry = KnowledgeService.update_entry(
            self.entry2, {'title': 'Updated Title'}, self.user
        )
        self.assertEqual(entry.title, 'Updated Title')
        self.assertEqual(entry.updated_by, self.user)

    def test_update_entry_invalid_field(self):
        with self.assertRaises(ValueError):
            KnowledgeService.update_entry(
                self.entry2, {'status': 'published'}, self.user
            )

    def test_delete_entry(self):
        KnowledgeService.delete_entry(self.entry1, self.user)
        self.entry1.refresh_from_db()
        self.assertTrue(self.entry1.is_deleted)
        self.assertIsNotNone(self.entry1.deleted_at)
        self.assertEqual(self.entry1.updated_by, self.user)

    def test_restore_entry(self):
        KnowledgeService.restore_entry(self.entry3, self.user)
        self.entry3.refresh_from_db()
        self.assertFalse(self.entry3.is_deleted)
        self.assertIsNone(self.entry3.deleted_at)
        self.assertEqual(self.entry3.updated_by, self.user)

    def test_publish_entry(self):
        entry = KnowledgeService.publish_entry(self.entry2, self.user)
        self.assertEqual(entry.status, 'published')
        self.assertIsNotNone(entry.published_at)
        self.assertEqual(entry.updated_by, self.user)

    def test_unpublish_entry_preserves_published_at(self):
        published_at = self.entry1.published_at
        entry = KnowledgeService.unpublish_entry(self.entry1, self.user)
        self.assertEqual(entry.status, 'draft')
        self.assertEqual(entry.published_at, published_at)

    def test_archive_entry_preserves_published_at(self):
        published_at = self.entry1.published_at
        entry = KnowledgeService.archive_entry(self.entry1, self.user)
        self.assertEqual(entry.status, 'archived')
        self.assertEqual(entry.published_at, published_at)

    def test_get_category_as_text(self):
        text = KnowledgeService.get_category_as_text('faq')
        self.assertIn('FAQ 1', text)
        self.assertIn('Answer 1', text)

    def test_get_category_as_text_empty(self):
        text = KnowledgeService.get_category_as_text('technology')
        self.assertEqual(text, '')

    def test_get_scoped_knowledge_as_text(self):
        # Create a published service entry
        KnowledgeEntry.objects.create(
            category='company', title='Company Info', content='We are B10',
            status='published',
        )
        text = KnowledgeService.get_scoped_knowledge_as_text(
            company=True, services=False, industries=False, faq=True, contact=False
        )
        self.assertIn('Company Information:', text)
        self.assertIn('Frequently Asked Questions (FAQ):', text)
        self.assertNotIn('Services Provided:', text)
        self.assertNotIn('Industries Served:', text)
        self.assertNotIn('Contact Information:', text)

    def test_get_scoped_knowledge_as_text_json_indent(self):
        KnowledgeEntry.objects.create(
            category='service', title='Mobile Dev', content='We build apps',
            status='published',
        )
        text = KnowledgeService.get_scoped_knowledge_as_text(
            company=False, services=True, industries=False, faq=False, contact=False
        )
        # Verify indent=2 JSON formatting
        self.assertIn('  "title"', text)


class KnowledgeEntrySerializerTests(TestCase):
    """Tests for serializers."""

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='pass')
        self.entry = KnowledgeEntry.objects.create(
            category='faq',
            title='Test FAQ',
            content='Test answer',
            status='published',
            created_by=self.user,
        )

    def test_list_serializer_fields(self):
        serializer = KnowledgeEntryListSerializer(self.entry)
        data = serializer.data
        self.assertIn('id', data)
        self.assertIn('category', data)
        self.assertIn('title', data)
        self.assertIn('slug', data)
        self.assertIn('status', data)
        self.assertIn('source', data)
        self.assertNotIn('content', data)
        self.assertNotIn('is_deleted', data)

    def test_detail_serializer_includes_content(self):
        serializer = KnowledgeEntryDetailSerializer(self.entry)
        data = serializer.data
        self.assertIn('content', data)
        self.assertIn('structured_data', data)
        self.assertEqual(data['created_by'], 'testuser')
        self.assertIsNone(data['updated_by'])
        self.assertNotIn('is_deleted', data)
        self.assertNotIn('deleted_at', data)

    def test_write_serializer_valid(self):
        serializer = KnowledgeEntryWriteSerializer(data={
            'category': 'faq',
            'title': 'New Question',
        })
        self.assertTrue(serializer.is_valid())

    def test_write_serializer_invalid_category(self):
        serializer = KnowledgeEntryWriteSerializer(data={
            'category': 'invalid',
            'title': 'Test',
        })
        self.assertFalse(serializer.is_valid())
        self.assertIn('category', serializer.errors)

    def test_write_serializer_partial(self):
        serializer = KnowledgeEntryWriteSerializer(
            data={'title': 'Updated'}, partial=True
        )
        self.assertTrue(serializer.is_valid())

    def test_write_serializer_invalid_source(self):
        serializer = KnowledgeEntryWriteSerializer(data={
            'category': 'faq',
            'title': 'Test',
            'source': 'unknown',
        })
        self.assertFalse(serializer.is_valid())
        self.assertIn('source', serializer.errors)
