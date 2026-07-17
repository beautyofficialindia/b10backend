import uuid
from django.db import models
from django.conf import settings


class Notification(models.Model):
    """
    Platform activity log and actionable alert for B10 administrators.

    Design rules:
    - Read-only after creation except for the is_read flag.
    - actor: who performed the action (nullable for system-generated events).
    - recipient: who the notification is addressed to (nullable, unused in V1;
      reserved for per-user notification scoping in future phases).
    """

    class Type(models.TextChoices):
        INFO = 'INFO', 'Info'
        SUCCESS = 'SUCCESS', 'Success'
        NOTICE = 'NOTICE', 'Notice'
        WARNING = 'WARNING', 'Warning'
        CRITICAL = 'CRITICAL', 'Critical'

    class Category(models.TextChoices):
        SYSTEM = 'SYSTEM', 'System'
        CRM = 'CRM', 'CRM'
        LEADS = 'LEADS', 'Leads'
        KNOWLEDGE = 'KNOWLEDGE', 'Knowledge'
        USERS = 'USERS', 'Users'
        ROLES = 'ROLES', 'Roles'
        SETTINGS = 'SETTINGS', 'Settings'
        ANALYTICS = 'ANALYTICS', 'Analytics'
        AI = 'AI', 'AI'
        AUTHENTICATION = 'AUTHENTICATION', 'Authentication'
        DEPLOYMENT = 'DEPLOYMENT', 'Deployment'
        SECURITY = 'SECURITY', 'Security'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    message = models.TextField()
    type = models.CharField(max_length=20, choices=Type.choices, default=Type.INFO)
    category = models.CharField(max_length=20, choices=Category.choices, default=Category.SYSTEM)

    # Relative path for Next.js navigation, e.g. /crm/lead/123 or /settings?group=CRM
    # CharField is intentional: URLField requires http(s):// and rejects relative paths.
    action_url = models.CharField(max_length=500, blank=True, default='')

    is_read = models.BooleanField(default=False)

    # Who triggered the action (null for system-generated notifications)
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='notifications_as_actor',
    )

    # Who the notification is addressed to (null = platform-wide in V1)
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='notifications_as_recipient',
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'

    def __str__(self):
        return f'[{self.type}] {self.title}'
