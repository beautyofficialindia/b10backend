from django.conf import settings
from django.db import models


class Setting(models.Model):
    """Generic key-value settings store with JSON values."""

    CATEGORY_CHOICES = [
        ('GENERAL', 'General'),
        ('BRANDING', 'Branding'),
        ('AI', 'AI'),
        ('CHATBOT', 'Chatbot'),
        ('NOTIFICATIONS', 'Notifications'),
        ('SECURITY', 'Security'),
        ('FEATURE_FLAGS', 'Feature Flags'),
        ('INTEGRATIONS', 'Integrations'),
    ]

    id = models.BigAutoField(primary_key=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    key = models.CharField(max_length=100)
    value = models.JSONField(default=None, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    is_public = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='settings_updated',
    )

    class Meta:
        app_label = 'settings_management'
        unique_together = [('category', 'key')]
        ordering = ['category', 'key']
        indexes = [
            models.Index(fields=['category']),
            models.Index(fields=['category', 'key']),
            models.Index(fields=['is_public']),
        ]

    def __str__(self):
        return f"{self.category}.{self.key}"
