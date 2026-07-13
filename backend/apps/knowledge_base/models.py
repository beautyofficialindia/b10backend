import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.text import slugify
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, db_index=True)
    description = models.TextField(blank=True)
    color = models.CharField(max_length=20, default="#3b82f6")
    icon = models.CharField(max_length=50, blank=True)
    sort_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['sort_order', 'name']

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True, db_index=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class KnowledgeEntry(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]

    SOURCE_CHOICES = [
        ('manual', 'Manual'),
        ('json_import', 'JSON Import'),
        ('api', 'API'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='entries'
    )
    tags = models.ManyToManyField(Tag, blank=True, related_name='entries')
    title = models.CharField(max_length=255, blank=False, null=False)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    content = models.TextField(blank=False, null=False, default='')
    structured_data = models.JSONField(default=dict, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    sort_order = models.PositiveIntegerField(default=0)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='kb_entries_created',
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='kb_entries_updated',
    )
    published_at = models.DateTimeField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES, default='manual')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['category', 'sort_order', 'created_at']
        verbose_name_plural = 'Knowledge Entries'

    def __str__(self):
        return f"[{self.category.name}] {self.title}"

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title)
            if not base:
                base = 'entry'
            candidate = base
            if KnowledgeEntry.objects.filter(slug=candidate).exclude(pk=self.pk).exists():
                candidate = f"{base}-{uuid.uuid4().hex[:8]}"
            self.slug = candidate

        if self.status == 'published' and self.published_at is None:
            self.published_at = timezone.now()

        if self.is_deleted and self.deleted_at is None:
            self.deleted_at = timezone.now()

        super().save(*args, **kwargs)


from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=KnowledgeEntry)
def knowledge_entry_post_save(sender, instance, created, **kwargs):
    # Future versioning hook (Phase 10.4)
    pass

