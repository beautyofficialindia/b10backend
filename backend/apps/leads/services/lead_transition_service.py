from django.utils import timezone
from apps.leads.models import LeadEvent
from apps.leads.services.notification_service import NotificationService
from apps.analytics.services.analytics_service import AnalyticsService
from apps.crm.services.crm_service import CRMService


class LeadTransitionService:
    """
    Single orchestrator for all Lead status-change side effects.

    Architectural rule:
        After any Lead status transition, the caller must invoke
        LeadTransitionService.on_status_changed(lead, old_status, new_status).
        No other service or view should independently trigger notifications,
        analytics, or CRM logs for a status change.

    This service owns WHAT HAPPENS AFTER a status changes.
    QualificationService owns WHETHER a lead is qualified and the mechanical transition.
    """

    @staticmethod
    def on_status_changed(lead, old_status, new_status):
        """
        Dispatch downstream side effects for any Lead status transition.
        Safe to call even if old_status == new_status (no-op in that case).
        """
        if old_status == new_status:
            return

        # Always log the status change and CRM activity
        CRMService.log_status_change(lead, old_status, new_status)

        if new_status == 'qualified':
            LeadTransitionService._on_qualified(lead)
        elif new_status == 'converted':
            AnalyticsService.track_lead_converted(lead)
        elif new_status == 'lost':
            AnalyticsService.track_lead_lost(lead)

    @staticmethod
    def _on_qualified(lead):
        """
        Side effects specific to the gathering -> qualified transition.
        Called only when the lead is newly qualified.
        """
        LeadEvent.objects.create(
            lead=lead,
            event_type='lead_qualified',
            metadata={'old_status': 'gathering', 'new_status': 'qualified'},
        )
        AnalyticsService.track_lead_qualified(lead)

        # NotificationService has its own idempotency guard (notification_sent boolean).
        # That guard is the safety net; this method should only be called on a true transition.
        notification_service = NotificationService()
        notification_service.send_lead_notification(lead)
