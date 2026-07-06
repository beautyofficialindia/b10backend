from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Lead, LeadEvent


@receiver(post_save, sender=Lead)
def track_escalated_lead_event(sender, instance, created, **kwargs):
    if created or instance.status != 'escalated':
        return
    exists = instance.lead_events.filter(event_type='escalation_triggered').exists()
    if not exists:
        LeadEvent.objects.create(
            lead=instance,
            event_type='escalation_triggered',
            metadata={"status": instance.status},
        )
