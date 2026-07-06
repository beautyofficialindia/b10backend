from .models import Lead
from .services.notification_service import NotificationService


def notify_sales_new_qualified_lead(lead_id):
    lead = Lead.objects.get(id=lead_id)
    return NotificationService().send_lead_notification(lead)


def notify_sales_of_escalation(lead_id):
    lead = Lead.objects.get(id=lead_id)
    return NotificationService().send_lead_notification(lead)
