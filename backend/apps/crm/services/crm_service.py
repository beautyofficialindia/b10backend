from ..models import LeadActivity, LeadStatusHistory
from django.utils import timezone


class CRMService:
    @staticmethod
    def log_activity(lead, activity_type, notes=None):
        return LeadActivity.objects.create(
            lead=lead,
            activity_type=activity_type,
            notes=notes
        )

    @staticmethod
    def log_status_change(lead, old_status, new_status):
        LeadStatusHistory.objects.create(
            lead=lead,
            old_status=old_status,
            new_status=new_status
        )
        CRMService.log_activity(
            lead, 
            'status_changed', 
            f"Status changed from {old_status} to {new_status}"
        )

    @staticmethod
    def touch_last_contacted(lead):
        """
        Updates last_contacted_at to now. Must only be called for genuine
        customer-facing or sales interactions (follow-ups, notes, manual outreach).
        Must NOT be called for internal system notifications or automated bot replies.
        """
        lead.last_contacted_at = timezone.now()
        lead.save(update_fields=['last_contacted_at'])

