from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.knowledge_base.models import KnowledgeEntry, Category, Tag
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
            category=Category.objects.get_or_create(slug='faq', defaults={'name':'faq'})[0], title='How to Reset Password', content='Go to settings.'
        )
        self.assertEqual(entry.slug, 'how-to-reset-password')

    def test_slug_collision_appends_uuid_suffix(self):
        KnowledgeEntry.objects.create(
            category=Category.objects.get_or_create(slug='faq', defaults={'name':'faq'})[0], title='Test Entry', content='First'
        )
        entry2 = KnowledgeEntry.objects.create(
            category=Category.objects.get_or_create(slug='faq', defaults={'name':'faq'})[0], title='Test Entry', content='Second'
        )
        self.assertTrue(entry2.slug.startswith('test-entry-'))
        self.assertNotEqual(entry2.slug, 'test-entry')
        self.assertEqual(len(entry2.slug), len('test-entry-') + 8)

    def test_published_at_auto_stamped_on_first_publish(self):
        entry = KnowledgeEntry.objects.create(
            category=Category.objects.get_or_create(slug='faq', defaults={'name':'faq'})[0], title='Pub Test', content='x'
        )
        self.assertIsNone(entry.published_at)
        entry.status = 'published'
        entry.save()
        entry.refresh_from_db()
        self.assertIsNotNone(entry.published_at)

    def test_published_at_not_overwritten_on_re_publish(self):
        entry = KnowledgeEntry.objects.create(
            category=Category.objects.get_or_create(slug='faq', defaults={'name':'faq'})[0], title='Re-Pub Test', content='x', status='published'
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
            category=Category.objects.get_or_create(slug='faq', defaults={'name':'faq'})[0], title='Del Test', content='x'
        )
        self.assertIsNone(entry.deleted_at)
        entry.is_deleted = True
        entry.save()
        entry.refresh_from_db()
        self.assertIsNotNone(entry.deleted_at)

    def test_str_format(self):
        entry = KnowledgeEntry(category=Category.objects.get_or_create(slug='service', defaults={'name':'service'})[0], title='Web Development')
        self.assertEqual(str(entry), '[service] Web Development')

    def test_meta_ordering(self):
        self.assertEqual(
            KnowledgeEntry._meta.ordering,
            ['category', 'sort_order', 'created_at'],
        )


class KnowledgeServiceTests(TestCase):
    """Tests for KnowledgeService."""

    def setUp(self):
        self.cat_faq, _ = Category.objects.get_or_create(name='FAQ', slug='faq')
        self.cat_service, _ = Category.objects.get_or_create(name='Service', slug='service')
        self.cat_company, _ = Category.objects.get_or_create(name='Company', slug='company')
        self.cat_industry, _ = Category.objects.get_or_create(name='Industry', slug='industry')
        self.cat_technology, _ = Category.objects.get_or_create(name='Technology', slug='technology')
        self.cat_contact, _ = Category.objects.get_or_create(name='Contact', slug='contact')

        self.user = User.objects.create_user(username='admin', password='pass')
        self.entry1 = KnowledgeEntry.objects.create(
            category=Category.objects.get_or_create(slug='faq', defaults={'name':'faq'})[0], title='FAQ 1', content='Answer 1', status='published'
        )
        self.entry2 = KnowledgeEntry.objects.create(
            category=Category.objects.get_or_create(slug='service', defaults={'name':'service'})[0], title='Web Dev', content='We build web apps', status='draft'
        )
        self.entry3 = KnowledgeEntry.objects.create(
            category=Category.objects.get_or_create(slug='faq', defaults={'name':'faq'})[0], title='FAQ 2', content='Answer 2', status='published', is_deleted=True
        )
        self.entry4 = KnowledgeEntry.objects.create(
            category=Category.objects.get_or_create(slug='faq', defaults={'name':'faq'})[0], title='FAQ 3', content='Answer 3', status='archived'
        )

    def test_list_entries_no_filter(self):
        entries = KnowledgeService.list_entries()
        # Excludes soft-deleted by default, but includes archived
        self.assertEqual(entries.count(), 3)

    def test_list_entries_category_filter(self):
        entries = KnowledgeService.list_entries(category='faq')
        # faq has entry1 and entry4
        self.assertEqual(entries.count(), 2)

    def test_list_entries_search_filter(self):
        entries = KnowledgeService.list_entries(search='web')
        self.assertEqual(entries.count(), 1)
        self.assertEqual(entries.first().pk, self.entry2.pk)

    def test_list_entries_search_whitespace_ignored(self):
        entries = KnowledgeService.list_entries(search='   ')
        self.assertEqual(entries.count(), 3)

    def test_list_entries_search_ranking(self):
        KnowledgeEntry.objects.create(
            category=Category.objects.get_or_create(slug='faq', defaults={'name':'faq'})[0], title='Web Web Web', content='Nothing', status='published'
        )
        KnowledgeEntry.objects.create(
            category=Category.objects.get_or_create(slug='faq', defaults={'name':'faq'})[0], title='Something Else', content='web', status='published'
        )
        entries = KnowledgeService.list_entries(search='web')
        self.assertTrue(entries.count() >= 2)
        self.assertEqual(entries.first().title, 'Web Web Web')

    def test_list_entries_search_and_ordering(self):
        KnowledgeEntry.objects.create(
            category=Category.objects.get_or_create(slug='faq', defaults={'name':'faq'})[0], title='A Web', content='', status='published', sort_order=100
        )
        KnowledgeEntry.objects.create(
            category=Category.objects.get_or_create(slug='faq', defaults={'name':'faq'})[0], title='Z Web Web', content='', status='published', sort_order=1
        )
        entries = KnowledgeService.list_entries(search='Web', ordering='sort_order')
        self.assertEqual(entries.first().title, 'Z Web Web')

    def test_list_entries_ordering_no_search(self):
        entries = KnowledgeService.list_entries(ordering='title')
        self.assertTrue(entries.first().title < entries.last().title)

    def test_list_entries_status_filter(self):
        entries = KnowledgeService.list_entries(status='published')
        self.assertEqual(entries.count(), 1)
        self.assertEqual(entries.first().pk, self.entry1.pk)

    def test_list_entries_include_deleted(self):
        entries = KnowledgeService.list_entries(include_deleted=True)
        self.assertEqual(entries.count(), 4)

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
            data={'category': Category.objects.get_or_create(slug='faq')[0], 'title': 'New FAQ', 'content': 'Answer'},
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
            KnowledgeService.create_entry(data={'category': Category.objects.get_or_create(slug='faq')[0]}, user=self.user)
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
        KnowledgeService.restore_entry(self.entry4, self.user)
        self.entry4.refresh_from_db()
        self.assertEqual(self.entry4.status, 'draft')
        self.assertEqual(self.entry4.updated_by, self.user)

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
            category=Category.objects.get_or_create(slug='company', defaults={'name':'company'})[0], title='Company Info', content='We are B10',
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
            category=Category.objects.get_or_create(slug='service', defaults={'name':'service'})[0], title='Mobile Dev', content='We build apps',
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
        self.cat_faq, _ = Category.objects.get_or_create(name='FAQ', slug='faq')
        self.cat_service, _ = Category.objects.get_or_create(name='Service', slug='service')
        self.cat_company, _ = Category.objects.get_or_create(name='Company', slug='company')
        self.cat_industry, _ = Category.objects.get_or_create(name='Industry', slug='industry')
        self.cat_technology, _ = Category.objects.get_or_create(name='Technology', slug='technology')
        self.cat_contact, _ = Category.objects.get_or_create(name='Contact', slug='contact')

        self.user = User.objects.create_user(username='testuser', password='pass')
        self.entry = KnowledgeEntry.objects.create(
            category=Category.objects.get_or_create(slug='faq', defaults={'name':'faq'})[0],
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
            'category': Category.objects.get_or_create(slug='faq')[0].id,
            'title': 'New Question',
        })
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_write_serializer_invalid_category(self):
        serializer = KnowledgeEntryWriteSerializer(data={
            'category': 99999,
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
            'category': Category.objects.get_or_create(slug='faq')[0].id,
            'title': 'Test',
            'source': 'unknown',
        })
        self.assertFalse(serializer.is_valid())
        self.assertIn('source', serializer.errors)


from django.contrib.auth.models import Group
from django.test import override_settings
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

NO_THROTTLE = {
    'DEFAULT_THROTTLE_CLASSES': [],
    'DEFAULT_THROTTLE_RATES': {},
}


@override_settings(REST_FRAMEWORK={**NO_THROTTLE})
class PublicEndpointTests(APITestCase):
    """Integration tests for public read endpoints."""

    def setUp(self):
        self.cat_faq, _ = Category.objects.get_or_create(name='FAQ', slug='faq')
        self.cat_service, _ = Category.objects.get_or_create(name='Service', slug='service')
        self.cat_company, _ = Category.objects.get_or_create(name='Company', slug='company')
        self.cat_industry, _ = Category.objects.get_or_create(name='Industry', slug='industry')
        self.cat_technology, _ = Category.objects.get_or_create(name='Technology', slug='technology')
        self.cat_contact, _ = Category.objects.get_or_create(name='Contact', slug='contact')

        self.published = KnowledgeEntry.objects.create(
            category=Category.objects.get_or_create(slug='faq', defaults={'name':'faq'})[0], title='Public FAQ', content='Public answer', status='published'
        )
        self.draft = KnowledgeEntry.objects.create(
            category=Category.objects.get_or_create(slug='faq', defaults={'name':'faq'})[0], title='Draft FAQ', content='Draft answer', status='draft'
        )
        self.deleted = KnowledgeEntry.objects.create(
            category=Category.objects.get_or_create(slug='faq', defaults={'name':'faq'})[0], title='Deleted FAQ', content='Deleted answer',
            status='published', is_deleted=True
        )

    def test_list_returns_only_published_non_deleted(self):
        response = self.client.get('/api/v1/kb/entries/')
        self.assertEqual(response.status_code, 200)
        data = response.json()['data']
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['title'], 'Public FAQ')

    def test_list_category_filter(self):
        KnowledgeEntry.objects.create(
            category=Category.objects.get_or_create(slug='service', defaults={'name':'service'})[0], title='Web Dev', content='apps', status='published'
        )
        response = self.client.get('/api/v1/kb/entries/?category=service')
        self.assertEqual(response.status_code, 200)
        data = response.json()['data']
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['category']['slug'], 'service')

    def test_list_search_filter(self):
        response = self.client.get('/api/v1/kb/entries/?search=Public')
        self.assertEqual(response.status_code, 200)
        data = response.json()['data']
        self.assertEqual(len(data), 1)

    def test_detail_published_200(self):
        response = self.client.get(f'/api/v1/kb/entries/{self.published.slug}/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['data']['title'], 'Public FAQ')

    def test_detail_draft_404(self):
        response = self.client.get(f'/api/v1/kb/entries/{self.draft.slug}/')
        self.assertEqual(response.status_code, 404)

    def test_detail_deleted_404(self):
        response = self.client.get(f'/api/v1/kb/entries/{self.deleted.slug}/')
        self.assertEqual(response.status_code, 404)

    def test_detail_nonexistent_404(self):
        response = self.client.get('/api/v1/kb/entries/nonexistent-slug/')
        self.assertEqual(response.status_code, 404)

    def test_pagination_metadata(self):
        response = self.client.get('/api/v1/kb/entries/')
        self.assertEqual(response.status_code, 200)
        meta = response.json().get('meta', {})
        self.assertIn('pagination', meta)
        pagination = meta['pagination']
        self.assertIn('page', pagination)
        self.assertIn('page_size', pagination)
        self.assertIn('total_count', pagination)
        self.assertIn('total_pages', pagination)


@override_settings(REST_FRAMEWORK={**NO_THROTTLE})
class AdminEndpointTests(APITestCase):
    """Integration tests for admin CRUD and status transition endpoints."""

    def setUp(self):
        self.cat_faq, _ = Category.objects.get_or_create(name='FAQ', slug='faq')
        self.cat_service, _ = Category.objects.get_or_create(name='Service', slug='service')
        self.cat_company, _ = Category.objects.get_or_create(name='Company', slug='company')
        self.cat_industry, _ = Category.objects.get_or_create(name='Industry', slug='industry')
        self.cat_technology, _ = Category.objects.get_or_create(name='Technology', slug='technology')
        self.cat_contact, _ = Category.objects.get_or_create(name='Contact', slug='contact')

        # Create admin user
        self.admin_user = User.objects.create_user(username='admin_user', password='pass')
        admin_group = Group.objects.create(name='Admin')
        self.admin_user.groups.add(admin_group)

        # Create non-admin user
        self.sales_user = User.objects.create_user(username='sales_user', password='pass')
        sales_group = Group.objects.create(name='Sales')
        self.sales_user.groups.add(sales_group)

        # Create entry
        self.entry = KnowledgeEntry.objects.create(
            category=Category.objects.get_or_create(slug='service', defaults={'name':'service'})[0], title='Test Service', content='Description', status='draft'
        )

        # Get admin JWT token
        refresh = RefreshToken.for_user(self.admin_user)
        self.admin_token = str(refresh.access_token)

        refresh_sales = RefreshToken.for_user(self.sales_user)
        self.sales_token = str(refresh_sales.access_token)

    def _auth_headers(self, token):
        return {'HTTP_AUTHORIZATION': f'Bearer {token}'}

    def test_unauthenticated_401(self):
        response = self.client.get('/api/v1/admin/kb/entries/')
        self.assertEqual(response.status_code, 401)

    def test_non_admin_403(self):
        response = self.client.get(
            '/api/v1/admin/kb/entries/',
            **self._auth_headers(self.sales_token)
        )
        self.assertEqual(response.status_code, 403)

    def test_list_200(self):
        response = self.client.get(
            '/api/v1/admin/kb/entries/',
            **self._auth_headers(self.admin_token)
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()['data']
        self.assertEqual(len(data), 1)

    def test_create_valid_201(self):
        response = self.client.post(
            '/api/v1/admin/kb/entries/',
            data={'category': Category.objects.get_or_create(slug='faq')[0].id, 'title': 'New FAQ', 'content': 'Answer'},
            format='json',
            **self._auth_headers(self.admin_token)
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()['data']['status'], 'draft')
        self.assertEqual(response.json()['data']['created_by'], 'admin_user')

    def test_create_invalid_400(self):
        response = self.client.post(
            '/api/v1/admin/kb/entries/',
            data={'content': 'No category or title'},
            format='json',
            **self._auth_headers(self.admin_token)
        )
        self.assertEqual(response.status_code, 400)

    def test_retrieve_200(self):
        response = self.client.get(
            f'/api/v1/admin/kb/entries/{self.entry.pk}/',
            **self._auth_headers(self.admin_token)
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['data']['title'], 'Test Service')

    def test_partial_update_200(self):
        response = self.client.patch(
            f'/api/v1/admin/kb/entries/{self.entry.pk}/',
            data={'title': 'Updated Service'},
            format='json',
            **self._auth_headers(self.admin_token)
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['data']['title'], 'Updated Service')

    def test_soft_delete_204(self):
        response = self.client.delete(
            f'/api/v1/admin/kb/entries/{self.entry.pk}/',
            **self._auth_headers(self.admin_token)
        )
        self.assertEqual(response.status_code, 204)
        self.entry.refresh_from_db()
        self.assertTrue(self.entry.is_deleted)

    def test_publish_200(self):
        response = self.client.post(
            f'/api/v1/admin/kb/entries/{self.entry.pk}/publish/',
            **self._auth_headers(self.admin_token)
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['data']['status'], 'published')

    def test_unpublish_200(self):
        self.entry.status = 'published'
        self.entry.save()
        response = self.client.post(
            f'/api/v1/admin/kb/entries/{self.entry.pk}/unpublish/',
            **self._auth_headers(self.admin_token)
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['data']['status'], 'draft')

    def test_archive_200(self):
        response = self.client.post(
            f'/api/v1/admin/kb/entries/{self.entry.pk}/archive/',
            **self._auth_headers(self.admin_token)
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['data']['status'], 'archived')

    def test_restore_archived_200(self):
        self.entry.status = 'archived'
        self.entry.save()
        response = self.client.post(
            f'/api/v1/admin/kb/entries/{self.entry.pk}/restore/',
            **self._auth_headers(self.admin_token)
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['data']['status'], 'draft')

    def test_restore_non_archived_400(self):
        self.entry.status = 'draft'
        self.entry.save()
        response = self.client.post(
            f'/api/v1/admin/kb/entries/{self.entry.pk}/restore/',
            **self._auth_headers(self.admin_token)
        )
        self.assertEqual(response.status_code, 400)


    def test_nonexistent_uuid_404(self):
        import uuid
        fake_id = uuid.uuid4()
        response = self.client.get(
            f'/api/v1/admin/kb/entries/{fake_id}/',
            **self._auth_headers(self.admin_token)
        )
        self.assertEqual(response.status_code, 404)

    def test_status_filter(self):
        KnowledgeEntry.objects.create(
            category=Category.objects.get_or_create(slug='faq', defaults={'name':'faq'})[0], title='Published FAQ', content='x', status='published'
        )
        response = self.client.get(
            '/api/v1/admin/kb/entries/?status=published',
            **self._auth_headers(self.admin_token)
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()['data']
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['status'], 'published')

    def test_ordering(self):
        KnowledgeEntry.objects.create(
            category=Category.objects.get_or_create(slug='faq', defaults={'name':'faq'})[0], title='AAA', content='x', status='draft'
        )
        response = self.client.get(
            '/api/v1/admin/kb/entries/?ordering=title',
            **self._auth_headers(self.admin_token)
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()['data']
        self.assertEqual(data[0]['title'], 'AAA')


class ChatbotCompatibilityTests(TestCase):
    """Verify KnowledgeService output matches KnowledgeLoader format."""

    def test_scoped_knowledge_format(self):
        """get_scoped_knowledge_as_text produces correct section labels and JSON format."""
        KnowledgeEntry.objects.create(
            category=Category.objects.get_or_create(slug='company', defaults={'name':'company'})[0], title='Company Info',
            content='We are B10 IT Solution',
            structured_data={'name': 'B10 IT Solution', 'founded': 2020},
            status='published',
        )
        KnowledgeEntry.objects.create(
            category=Category.objects.get_or_create(slug='service', defaults={'name':'service'})[0], title='Web Development',
            content='Custom web apps',
            structured_data={'technologies': ['React', 'Django']},
            status='published',
        )

        text = KnowledgeService.get_scoped_knowledge_as_text(
            company=True, services=True, industries=False, faq=False, contact=False
        )

        # Verify section labels
        self.assertIn('Company Information:', text)
        self.assertIn('Services Provided:', text)

        # Verify omitted categories
        self.assertNotIn('Industries Served:', text)
        self.assertNotIn('Frequently Asked Questions (FAQ):', text)
        self.assertNotIn('Contact Information:', text)

        # Verify JSON formatting (indent=2)
        self.assertIn('  "title":', text)
        self.assertIn('  "content":', text)

        # Verify structured_data is merged into the dict
        self.assertIn('"name": "B10 IT Solution"', text)
        self.assertIn('"technologies"', text)

    def test_empty_category_omitted(self):
        """Categories with no published entries are omitted entirely."""
        text = KnowledgeService.get_scoped_knowledge_as_text(
            company=True, services=True, industries=True, faq=True, contact=True
        )
        self.assertEqual(text, '')

    def test_section_ordering(self):
        """Sections appear in correct order: company, services, industries, faq, contact."""
        for cat, title in [
            ('company', 'Co'), ('service', 'Svc'),
            ('industry', 'Ind'), ('faq', 'FAQ Q'), ('contact', 'Contact'),
        ]:
            cat_obj, _ = Category.objects.get_or_create(slug=cat, defaults={'name': cat})
            KnowledgeEntry.objects.create(
                category=cat_obj, title=title, content='text', status='published'
            )

        text = KnowledgeService.get_scoped_knowledge_as_text()

        company_pos = text.index('Company Information:')
        services_pos = text.index('Services Provided:')
        industries_pos = text.index('Industries Served:')
        faq_pos = text.index('Frequently Asked Questions (FAQ):')
        contact_pos = text.index('Contact Information:')

        self.assertLess(company_pos, services_pos)
        self.assertLess(services_pos, industries_pos)
        self.assertLess(industries_pos, faq_pos)
        self.assertLess(faq_pos, contact_pos)


class KnowledgeVersionServiceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='versionadmin', password='pw')
        self.category = Category.objects.create(name='Version Cat', slug='version-cat')
        self.tag1 = Tag.objects.create(name='VTag1', slug='vtag1')
        
    def test_version_created_on_mutation(self):
        # Create
        entry = KnowledgeService.create_entry(
            {'category': self.category, 'title': 'V1 Title', 'content': 'V1 Content', 'tags': [self.tag1]},
            self.user,
            'Initial create'
        )
        self.assertEqual(entry.versions.count(), 1)
        v1 = entry.versions.first()
        self.assertEqual(v1.version_number, 1)
        self.assertEqual(v1.change_summary, 'Initial create')
        self.assertEqual(v1.title, 'V1 Title')
        
        # Snapshot check
        self.assertEqual(v1.category_snapshot['slug'], 'version-cat')
        self.assertEqual(len(v1.tags_snapshot), 1)
        self.assertEqual(v1.tags_snapshot[0]['slug'], 'vtag1')

        # Update
        KnowledgeService.update_entry(
            entry,
            {'title': 'V2 Title', 'content': 'V2 Content'},
            self.user,
            'Updated title'
        )
        self.assertEqual(entry.versions.count(), 2)
        v2 = entry.versions.order_by('-version_number').first()
        self.assertEqual(v2.version_number, 2)
        self.assertEqual(v2.title, 'V2 Title')
        
        # Publish
        KnowledgeService.publish_entry(entry, self.user)
        self.assertEqual(entry.versions.count(), 3)
        v3 = entry.versions.order_by('-version_number').first()
        self.assertEqual(v3.status, 'published')
        self.assertEqual(v3.change_summary, 'Published entry')

    def test_restore_version(self):
        entry = KnowledgeService.create_entry(
            {'category': self.category, 'title': 'V1', 'content': 'Content 1'},
            self.user,
            'Initial'
        )
        v1 = entry.versions.first()
        
        KnowledgeService.update_entry(
            entry,
            {'title': 'V2', 'content': 'Content 2'},
            self.user,
            'Second'
        )
        self.assertEqual(entry.title, 'V2')
        self.assertEqual(entry.versions.count(), 2)
        
        # Restore V1
        from apps.knowledge_base.services.version_service import KnowledgeVersionService
        KnowledgeVersionService.restore_version(v1, self.user)
        
        entry.refresh_from_db()
        self.assertEqual(entry.title, 'V1')
        self.assertEqual(entry.content, 'Content 1')
        
        # Should have 3 versions now
        self.assertEqual(entry.versions.count(), 3)
        v3 = entry.versions.order_by('-version_number').first()
        self.assertEqual(v3.title, 'V1')
        self.assertEqual(v3.change_summary, 'Restored from Version 1')
