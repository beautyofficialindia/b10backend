"""
NotificationService
===================

The single entry point for all notification creation across the B10 platform.

Usage — other modules MUST use the service, never create Notification objects directly:

    from apps.notifications.services import NotificationService

    # Generic
    NotificationService.create(
        title="Lead Converted",
        message="John Doe has been marked as converted.",
        type=Notification.Type.SUCCESS,
        category=Notification.Category.LEADS,
        action_url="/crm/leads/abc123",
        actor=request.user,
    )

    # Shorthand helpers (preferred)
    NotificationService.create_success(
        title="Lead Converted",
        message="John Doe has been marked as converted.",
        category=Notification.Category.LEADS,
        action_url="/crm/leads/abc123",
        actor=request.user,
    )
"""

from django.utils import timezone
from datetime import timedelta

MAX_NOTIFICATIONS = 500
NOTIFICATION_TTL_DAYS = 90


class NotificationService:

    # ------------------------------------------------------------------
    # Creation
    # ------------------------------------------------------------------

    @classmethod
    def create(cls, title, message, type, category, action_url='', actor=None, recipient=None):
        """
        Create a notification and enforce the retention policy.
        This is the only correct way to create notifications.
        """
        from .models import Notification
        notification = Notification.objects.create(
            title=title,
            message=message,
            type=type,
            category=category,
            action_url=action_url,
            actor=actor,
            recipient=recipient,
        )
        cls._enforce_retention()
        return notification

    @classmethod
    def create_info(cls, title, message, category, action_url='', actor=None, recipient=None):
        """Create an INFO notification."""
        from .models import Notification
        return cls.create(title, message, Notification.Type.INFO, category, action_url, actor, recipient)

    @classmethod
    def create_success(cls, title, message, category, action_url='', actor=None, recipient=None):
        """Create a SUCCESS notification."""
        from .models import Notification
        return cls.create(title, message, Notification.Type.SUCCESS, category, action_url, actor, recipient)

    @classmethod
    def create_notice(cls, title, message, category, action_url='', actor=None, recipient=None):
        """Create a NOTICE notification for operational/administrative messages."""
        from .models import Notification
        return cls.create(title, message, Notification.Type.NOTICE, category, action_url, actor, recipient)

    @classmethod
    def create_warning(cls, title, message, category, action_url='', actor=None, recipient=None):
        """Create a WARNING notification."""
        from .models import Notification
        return cls.create(title, message, Notification.Type.WARNING, category, action_url, actor, recipient)

    @classmethod
    def create_critical(cls, title, message, category, action_url='', actor=None, recipient=None):
        """Create a CRITICAL notification."""
        from .models import Notification
        return cls.create(title, message, Notification.Type.CRITICAL, category, action_url, actor, recipient)

    # ------------------------------------------------------------------
    # Read state management
    # ------------------------------------------------------------------

    @classmethod
    def mark_read(cls, notification_id):
        """Mark a single notification as read."""
        from .models import Notification
        notification = Notification.objects.get(id=notification_id)
        if not notification.is_read:
            notification.is_read = True
            notification.save(update_fields=['is_read'])
        return notification

    @classmethod
    def mark_unread(cls, notification_id):
        """Mark a single notification as unread (re-flag for follow-up)."""
        from .models import Notification
        notification = Notification.objects.get(id=notification_id)
        if notification.is_read:
            notification.is_read = False
            notification.save(update_fields=['is_read'])
        return notification

    @classmethod
    def mark_all_read(cls):
        """Mark all unread notifications as read. Returns count updated."""
        from .models import Notification
        count = Notification.objects.filter(is_read=False).update(is_read=True)
        return count

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    @classmethod
    def get_unread_count(cls):
        """Return number of unread notifications."""
        from .models import Notification
        return Notification.objects.filter(is_read=False).count()

    @classmethod
    def get_notifications(cls, category=None):
        """Return notifications queryset, optionally filtered by category."""
        from .models import Notification
        qs = Notification.objects.select_related('actor', 'recipient').all()
        if category:
            qs = qs.filter(category=category)
        return qs

    # ------------------------------------------------------------------
    # Deletion
    # ------------------------------------------------------------------

    @classmethod
    def delete(cls, notification_id):
        """Delete a single notification. Returns True if deleted."""
        from .models import Notification
        count, _ = Notification.objects.filter(id=notification_id).delete()
        return count > 0

    @classmethod
    def delete_all_read(cls):
        """Delete all read notifications. Returns count deleted."""
        from .models import Notification
        count, _ = Notification.objects.filter(is_read=True).delete()
        return count

    # ------------------------------------------------------------------
    # Retention
    # ------------------------------------------------------------------

    @classmethod
    def cleanup_old_notifications(cls):
        """
        Public method for management commands or scheduled jobs.
        Deletes notifications older than NOTIFICATION_TTL_DAYS.
        Returns the count of deleted notifications.
        """
        from .models import Notification
        cutoff = timezone.now() - timedelta(days=NOTIFICATION_TTL_DAYS)
        count, _ = Notification.objects.filter(created_at__lt=cutoff).delete()
        return count

    @classmethod
    def _enforce_retention(cls):
        """
        Private. Called automatically after every create().

        Policy:
        1. Delete notifications older than NOTIFICATION_TTL_DAYS (90 days).
        2. If total > MAX_NOTIFICATIONS (500), delete the oldest excess records.

        This keeps the table lean without any cron job or Celery task.
        """
        from .models import Notification

        # 1. TTL cleanup
        cutoff = timezone.now() - timedelta(days=NOTIFICATION_TTL_DAYS)
        Notification.objects.filter(created_at__lt=cutoff).delete()

        # 2. Cap cleanup
        total = Notification.objects.count()
        if total > MAX_NOTIFICATIONS:
            excess = total - MAX_NOTIFICATIONS
            oldest_ids = list(
                Notification.objects
                .order_by('created_at')
                .values_list('id', flat=True)[:excess]
            )
            Notification.objects.filter(id__in=oldest_ids).delete()
