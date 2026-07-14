import logging

from django.db import transaction
from django.utils import timezone

from apps.knowledge_base.models import KnowledgeEntry, KnowledgeEntryVersion, Category, Tag


logger = logging.getLogger(__name__)


class KnowledgeVersionService:
    """
    Service responsible for creating, retrieving, and restoring KnowledgeEntry versions.
    """

    @staticmethod
    def create_version(entry: KnowledgeEntry, user, summary: str = None) -> KnowledgeEntryVersion:
        """
        Takes a snapshot of the current state of a KnowledgeEntry and creates a new KnowledgeEntryVersion.
        If summary is not provided or is empty, a default is used.
        """
        if not summary or not summary.strip():
            summary = "No summary provided"

        # Determine next version number
        last_version = entry.versions.order_by('-version_number').first()
        next_version_number = (last_version.version_number + 1) if last_version else 1

        category_snapshot = {}
        if entry.category_id:
            try:
                # We fetch category explicitly to ensure we have the latest name/slug
                category_snapshot = {
                    "id": entry.category.id,
                    "name": entry.category.name,
                    "slug": entry.category.slug
                }
            except Exception as e:
                logger.warning(f"Failed to create category snapshot for {entry.id}: {e}")

        tags_snapshot = []
        try:
            for tag in entry.tags.all():
                tags_snapshot.append({
                    "id": tag.id,
                    "name": tag.name,
                    "slug": tag.slug
                })
        except Exception as e:
            logger.warning(f"Failed to create tags snapshot for {entry.id}: {e}")

        version = KnowledgeEntryVersion.objects.create(
            knowledge_entry=entry,
            version_number=next_version_number,
            title=entry.title,
            content=entry.content,
            structured_data=entry.structured_data,
            status=entry.status,
            category_snapshot=category_snapshot,
            tags_snapshot=tags_snapshot,
            created_by=user,
            change_summary=summary,
        )

        return version

    @staticmethod
    @transaction.atomic
    def restore_version(version: KnowledgeEntryVersion, user) -> KnowledgeEntry:
        """
        Restores a KnowledgeEntry to the state of a specific version.
        This modifies the KnowledgeEntry and immediately creates a new version snapshot
        to preserve the forward-only immutability.
        """
        entry = version.knowledge_entry

        entry.title = version.title
        entry.content = version.content
        entry.structured_data = version.structured_data
        entry.status = version.status

        # Resolve category by slug, fallback to ID, fallback to original if not found
        category_snapshot = version.category_snapshot
        if category_snapshot:
            slug = category_snapshot.get('slug')
            cat = Category.objects.filter(slug=slug).first() if slug else None
            if cat:
                entry.category = cat

        # Tags need to be saved after the entry is saved, but we'll collect them first
        tags_to_set = []
        for tag_snap in version.tags_snapshot:
            slug = tag_snap.get('slug')
            tag = Tag.objects.filter(slug=slug).first() if slug else None
            if tag:
                tags_to_set.append(tag)

        entry.updated_by = user
        entry.updated_at = timezone.now()
        entry.save()
        
        # Now set the tags
        if tags_to_set:
            entry.tags.set(tags_to_set)
        else:
            entry.tags.clear()
        
        summary = f"Restored from Version {version.version_number}"
        KnowledgeVersionService.create_version(entry, user, summary)

        return entry
