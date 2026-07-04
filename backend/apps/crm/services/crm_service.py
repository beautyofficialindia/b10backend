from ..models import LeadActivity, LeadStatusHistory

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
