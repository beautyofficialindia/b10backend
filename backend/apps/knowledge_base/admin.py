from django.contrib import admin
from django.db.models import F, Value
from django.db.models.functions import Coalesce
from django.utils import timezone

from apps.knowledge_base.models import KnowledgeEntry, Category, Tag, KnowledgeEntryVersion


@admin.register(KnowledgeEntry)
class KnowledgeAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'category', 'slug', 'status', 'is_deleted',
        'sort_order', 'created_at', 'updated_at',
    ]
    list_filter = ['category', 'status', 'is_deleted']
    search_fields = ['title', 'content']
    readonly_fields = [
        'id', 'slug', 'created_at', 'updated_at', 'published_at',
        'deleted_at', 'created_by', 'updated_by',
    ]
    ordering = ['category', 'sort_order', 'created_at']

    actions = ['publish_selected', 'unpublish_selected', 'archive_selected', 'restore_selected']

    @admin.action(description="Publish selected entries")
    def publish_selected(self, request, queryset):
        now = timezone.now()
        updated = queryset.filter(
            is_deleted=False
        ).exclude(status='published').update(
            status='published',
            published_at=Coalesce(F('published_at'), Value(now)),
            updated_by=request.user,
        )
        self.message_user(request, f"{updated} entries published.")

    @admin.action(description="Unpublish selected entries (set to Draft)")
    def unpublish_selected(self, request, queryset):
        updated = queryset.filter(is_deleted=False).exclude(status='draft').update(
            status='draft',
            updated_by=request.user,
        )
        self.message_user(request, f"{updated} entries unpublished.")

    @admin.action(description="Archive selected entries")
    def archive_selected(self, request, queryset):
        updated = queryset.filter(is_deleted=False).exclude(status='archived').update(
            status='archived',
            updated_by=request.user,
        )
        self.message_user(request, f"{updated} entries archived.")

    @admin.action(description="Restore selected soft-deleted entries")
    def restore_selected(self, request, queryset):
        updated = queryset.filter(is_deleted=True).update(
            is_deleted=False,
            deleted_at=None,
            updated_by=request.user,
        )
        self.message_user(request, f"{updated} entries restored.")


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'sort_order', 'is_active')
    search_fields = ('name', 'slug')


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_active')
    search_fields = ('name', 'slug')


@admin.register(KnowledgeEntryVersion)
class KnowledgeEntryVersionAdmin(admin.ModelAdmin):
    list_display = ('knowledge_entry', 'version_number', 'status', 'created_at', 'created_by')
    list_filter = ('status', 'created_at')
    search_fields = ('title', 'content', 'change_summary')
    readonly_fields = [
        'id', 'knowledge_entry', 'version_number', 'title', 'content',
        'structured_data', 'status', 'category_snapshot', 'tags_snapshot',
        'created_by', 'created_at', 'change_summary'
    ]
