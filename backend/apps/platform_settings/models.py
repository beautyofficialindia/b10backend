import uuid
from django.db import models
from django.conf import settings
from .constants import SettingGroup, ValueType

class PlatformSetting(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    group = models.CharField(max_length=50, choices=SettingGroup.CHOICES)
    key = models.CharField(max_length=100)
    display_name = models.CharField(max_length=255, blank=True)
    value = models.TextField(blank=True)
    value_type = models.CharField(max_length=20, choices=ValueType.CHOICES)
    
    description = models.TextField(blank=True)
    
    is_public = models.BooleanField(default=False)
    is_editable = models.BooleanField(default=True)
    is_sensitive = models.BooleanField(default=False)
    
    validation_rules = models.JSONField(default=dict, blank=True)
    display_order = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='updated_settings'
    )

    class Meta:
        unique_together = ('group', 'key')
        ordering = ['group', 'display_order', 'key']
        indexes = [
            models.Index(fields=['group']),
            models.Index(fields=['key']),
            models.Index(fields=['is_public']),
        ]
        permissions = [
            ("can_view_settings", "Can View Settings"),
            ("can_change_settings", "Can Change Settings"),
            ("can_initialize_settings", "Can Initialize Settings"),
        ]

    def __str__(self):
        return f"[{self.get_group_display()}] {self.display_name or self.key}"

    def save(self, *args, **kwargs):
        if not self.display_name:
            # Generate display name from key if not provided (e.g. DEFAULT_MODEL -> Default Model)
            self.display_name = self.key.replace('_', ' ').title()
        super().save(*args, **kwargs)
