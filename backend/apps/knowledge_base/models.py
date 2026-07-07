import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.text import slugify


class KnowledgeEntry(models.Model):
    CATEGORY_CHOICES = [
        ('company', 'Company Info'),
        ('service', 'Service'),
        ('industry', 'Industry'),
        ('faq', 'FAQ'),
        ('contact', 'Contact Info'),
        ('technology', 'Technology'),
        ('general', 'General'),
    ]

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
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
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
        return f"[{self.category}] {self.title}"

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
