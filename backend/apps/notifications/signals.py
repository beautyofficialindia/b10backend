"""
Notification Signals
====================

Reserved for future Django signal hooks that will connect platform events
to NotificationService.

V1: Notifications are created directly inside service layers:
    LeadService → NotificationService.create_success(...)
    SettingsService → NotificationService.create_notice(...)
    etc.

Future usage pattern:

    from django.db.models.signals import post_save
    from django.dispatch import receiver
    from apps.leads.models import Lead
    from apps.notifications.services import NotificationService

    @receiver(post_save, sender=Lead)
    def notify_lead_converted(sender, instance, created, **kwargs):
        if not created and instance.status == 'converted':
            NotificationService.create_success(
                title="Lead Converted",
                message=f"{instance.full_name or instance.email} has been converted.",
                category="LEADS",
                action_url=f"/crm/leads/{instance.id}",
            )
"""
