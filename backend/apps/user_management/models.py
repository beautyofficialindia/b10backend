from django.conf import settings
from django.db import models


class UserAuditLog(models.Model):
    """Records all state-changing operations on backend users."""

    id = models.BigAutoField(primary_key=True)
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='audit_actions_performed',
        help_text="Admin who performed the action",
    )
    target_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='audit_log_entries',
        help_text="User who was acted upon",
    )
    action = models.CharField(
        max_length=50,
        help_text="Action type identifier",
    )
    description = models.TextField(
        help_text="Human-readable description of the change",
    )
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Extensible data: IP, user agent, old/new values",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'user_management'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['target_user', '-created_at']),
            models.Index(fields=['actor', '-created_at']),
            models.Index(fields=['action']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        return f"{self.action} on user {self.target_user_id} by {self.actor_id} at {self.created_at}"
