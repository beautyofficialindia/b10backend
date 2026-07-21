import json

from django.db.models import Q
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from django.utils import timezone

from apps.knowledge_base.models import KnowledgeEntry
from apps.knowledge_base.services.version_service import KnowledgeVersionService


def _notify_knowledge(title, message, type_, entry_id, actor=None):
    """Fire-and-forget admin notification for knowledge base events."""
    try:
        from apps.notifications.services import NotificationService
        NotificationService.create(
            title=title,
            message=message,
            type=type_,
            category='KNOWLEDGE',
            action_url=f'/knowledge/{entry_id}',
            actor=actor,
        )
    except Exception:
        pass


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
    def _save_and_version(entry, user, summary=None, tags=None):
        """Helper to save the entry, apply tags if any, and create a version snapshot."""
        entry.save()
        if tags is not None:
            entry.tags.set(tags)
        KnowledgeVersionService.create_version(entry, user, summary)

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
    def create_entry(data, user, summary="Created initial version"):
        """
        Create a new KnowledgeEntry. Raises ValueError if category or title missing.
        """
        if not data.get('category'):
            raise ValueError("The 'category' field is required.")
        if not data.get('title'):
            raise ValueError("The 'title' field is required.")

        tags = data.pop('tags', None)
        if tags is None:
            tags = []
            
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
        KnowledgeService._save_and_version(entry, user, summary, tags=tags)
        return entry

    @staticmethod
    def update_entry(entry, data, user, summary="Updated entry"):
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
        KnowledgeService._save_and_version(entry, user, summary, tags=tags)
        return entry

    @staticmethod
    def delete_entry(entry, user, summary="Deleted entry (Soft Delete)"):
        """Soft-delete: set is_deleted=True, deleted_at, updated_by."""
        entry.is_deleted = True
        entry.deleted_at = timezone.now()
        entry.updated_by = user
        KnowledgeService._save_and_version(entry, user, summary)

    @staticmethod
    def restore_entry(entry, user, summary="Restored archived entry"):
        """Restore an archived entry to draft."""
        entry.status = 'draft'
        entry.updated_by = user
        KnowledgeService._save_and_version(entry, user, summary)
        _notify_knowledge(
            title='Knowledge Article Restored',
            message=f"'{entry.title}' has been restored to drafts.",
            type_='NOTICE',
            entry_id=entry.pk,
            actor=user,
        )
        return entry

    @staticmethod
    def publish_entry(entry, user, summary="Published entry"):
        """Set status to published. published_at set only if currently None."""
        entry.status = 'published'
        entry.updated_by = user
        # published_at is auto-set in model save() if None
        KnowledgeService._save_and_version(entry, user, summary)
        _notify_knowledge(
            title='Knowledge Article Published',
            message=f"'{entry.title}' has been published to the knowledge base.",
            type_='SUCCESS',
            entry_id=entry.pk,
            actor=user,
        )
        return entry

    @staticmethod
    def unpublish_entry(entry, user, summary="Unpublished entry"):
        """Set status to draft. published_at is NOT cleared."""
        entry.status = 'draft'
        entry.updated_by = user
        KnowledgeService._save_and_version(entry, user, summary)
        _notify_knowledge(
            title='Knowledge Article Unpublished',
            message=f"'{entry.title}' has been moved back to draft.",
            type_='NOTICE',
            entry_id=entry.pk,
            actor=user,
        )
        return entry

    @staticmethod
    def archive_entry(entry, user, summary="Archived entry"):
        """Set status to archived. published_at is NOT cleared."""
        entry.status = 'archived'
        entry.updated_by = user
        KnowledgeService._save_and_version(entry, user, summary)
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
