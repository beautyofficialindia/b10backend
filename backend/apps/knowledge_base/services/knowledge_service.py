import json

from django.db.models import Q
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from django.utils import timezone

from apps.knowledge_base.models import KnowledgeEntry


ALLOWED_ORDERING_VALUES = [
    'created_at', '-created_at',
    'sort_order', '-sort_order',
    'title', '-title',
]

ALLOWED_WRITABLE_FIELDS = ['category', 'tags', 'title', 'content', 'structured_data', 'sort_order']

SECTION_MAP = [
    ('company', 'company', 'Company Information'),
    ('services', 'service', 'Services Provided'),
    ('industries', 'industry', 'Industries Served'),
    ('faq', 'faq', 'Frequently Asked Questions (FAQ)'),
    ('contact', 'contact', 'Contact Information'),
]


class KnowledgeService:
    """Service class for all Knowledge Base data operations."""

    @staticmethod
    def list_entries(category=None, search=None, status=None, include_deleted=False, ordering=None):
        """
        Return a filtered QuerySet of KnowledgeEntry records.
        By default excludes soft-deleted entries.
        """
        qs = KnowledgeEntry.objects.select_related('category').prefetch_related('tags')

        if not include_deleted:
            qs = qs.filter(is_deleted=False)

        if category:
            qs = qs.filter(category__slug=category)

        if status:
            qs = qs.filter(status=status)

        if search and search.strip():
            # TODO: Add searching across Category and Tag names in future phases
            search = search.strip()
            vector = SearchVector('title', weight='A') + SearchVector('content', weight='B')
            query = SearchQuery(search)
            qs = qs.annotate(
                search_rank=SearchRank(vector, query)
            ).filter(search_rank__gte=0.01).order_by('-search_rank')
        elif ordering and ordering in ALLOWED_ORDERING_VALUES:
            qs = qs.order_by(ordering)

        return qs

    @staticmethod
    def get_entry(pk, include_deleted=False):
        """
        Return a single KnowledgeEntry or raise KnowledgeEntry.DoesNotExist.
        """
        qs = KnowledgeEntry.objects.select_related('category').prefetch_related('tags')
        if not include_deleted:
            qs = qs.filter(is_deleted=False)
        return qs.get(pk=pk)

    @staticmethod
    def create_entry(data, user):
        """
        Create a new KnowledgeEntry. Raises ValueError if category or title missing.
        """
        if not data.get('category'):
            raise ValueError("The 'category' field is required.")
        if not data.get('title'):
            raise ValueError("The 'title' field is required.")

        tags = data.pop('tags', [])
        entry = KnowledgeEntry(
            category=data['category'],
            title=data['title'],
            content=data.get('content', ''),
            structured_data=data.get('structured_data', {}),
            sort_order=data.get('sort_order', 0),
            source=data.get('source', 'manual'),
            status='draft',
            created_by=user,
        )
        entry.save()
        if tags:
            entry.tags.set(tags)
        return entry

    @staticmethod
    def update_entry(entry, data, user):
        """
        Update allowed fields on an existing entry. Raises ValueError for unrecognized fields.
        """
        for key in data:
            if key not in ALLOWED_WRITABLE_FIELDS:
                raise ValueError(f"Unrecognized or non-writable field: '{key}'")

        tags = data.pop('tags', None)
        for key, value in data.items():
            setattr(entry, key, value)

        entry.updated_by = user
        entry.save()
        if tags is not None:
            entry.tags.set(tags)
        return entry

    @staticmethod
    def delete_entry(entry, user):
        """Soft-delete: set is_deleted=True, deleted_at, updated_by."""
        entry.is_deleted = True
        entry.deleted_at = timezone.now()
        entry.updated_by = user
        entry.save()

    @staticmethod
    def restore_entry(entry, user):
        """Restore a soft-deleted entry."""
        entry.is_deleted = False
        entry.deleted_at = None
        entry.updated_by = user
        entry.save()
        return entry

    @staticmethod
    def publish_entry(entry, user):
        """Set status to published. published_at set only if currently None."""
        entry.status = 'published'
        entry.updated_by = user
        # published_at is auto-set in model save() if None
        entry.save()
        return entry

    @staticmethod
    def unpublish_entry(entry, user):
        """Set status to draft. published_at is NOT cleared."""
        entry.status = 'draft'
        entry.updated_by = user
        entry.save()
        return entry

    @staticmethod
    def archive_entry(entry, user):
        """Set status to archived. published_at is NOT cleared."""
        entry.status = 'archived'
        entry.updated_by = user
        entry.save()
        return entry

    @staticmethod
    def get_category_as_text(category):
        """
        Return a plain-text string of all published non-deleted entries for a category.
        Each entry: "{title}\n{content}", separated by "\n\n".
        Returns empty string if no entries.
        """
        entries = KnowledgeEntry.objects.filter(
            category__slug=category,
            status='published',
            is_deleted=False,
        ).order_by('sort_order', 'created_at')

        if not entries.exists():
            return ''

        return '\n\n'.join(f"{e.title}\n{e.content}" for e in entries)

    @staticmethod
    def get_scoped_knowledge_as_text(company=True, services=True, industries=True, faq=True, contact=True):
        """
        Produce format-identical output to KnowledgeLoader.get_scoped_knowledge_as_text.
        """
        flags = {
            'company': company,
            'services': services,
            'industries': industries,
            'faq': faq,
            'contact': contact,
        }
        text = ''
        for flag_key, category_value, label in SECTION_MAP:
            if not flags[flag_key]:
                continue
            entries = KnowledgeEntry.objects.filter(
                category__slug=category_value,
                status='published',
                is_deleted=False,
            ).order_by('sort_order', 'created_at')
            if not entries.exists():
                continue
            data = [
                {"title": e.title, "content": e.content, **e.structured_data}
                for e in entries
            ]
            text += f"{label}:\n{json.dumps(data, indent=2)}\n\n"
        return text
