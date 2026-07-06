from ..models import AnalyticsEvent
from django.utils import timezone


def _safe_metadata(metadata):
    metadata = metadata or {}
    blocked_keys = {"email", "phone", "full_name", "name", "company_name", "requirements"}
    return {key: value for key, value in metadata.items() if key not in blocked_keys}

class AnalyticsService:
    @staticmethod
    def track_event(event_type, conversation=None, lead=None, metadata=None):
        return AnalyticsEvent.objects.create(
            event_type=event_type,
            conversation=conversation,
            lead=lead,
            metadata=_safe_metadata(metadata),
            occurred_at=timezone.now()
        )

    @staticmethod
    def track_chat_started(conversation):
        return AnalyticsService.track_event('chat_started', conversation=conversation)

    @staticmethod
    def track_message_sent(conversation, role):
        return AnalyticsService.track_event('message_sent', conversation=conversation, metadata={"role": role})

    @staticmethod
    def track_lead_created(lead):
        return AnalyticsService.track_event('lead_created', conversation=lead.conversation, lead=lead)

    @staticmethod
    def track_lead_qualified(lead):
        return AnalyticsService.track_event('lead_qualified', conversation=lead.conversation, lead=lead)

    @staticmethod
    def track_email_notification_sent(lead):
        return AnalyticsService.track_event('email_notification_sent', conversation=lead.conversation, lead=lead)

    @staticmethod
    def track_lead_converted(lead):
        return AnalyticsService.track_event('lead_converted', conversation=lead.conversation, lead=lead)

    @staticmethod
    def track_lead_lost(lead):
        return AnalyticsService.track_event('lead_lost', conversation=lead.conversation, lead=lead)

    @staticmethod
    def track_scope_refusal(conversation, reason):
        return AnalyticsService.track_event('scope_refusal', conversation=conversation, metadata={"reason": reason})

    @staticmethod
    def track_escalation(conversation, reason, lead=None):
        return AnalyticsService.track_event(
            'escalation_triggered',
            conversation=conversation,
            lead=lead,
            metadata={"reason": reason}
        )

    @staticmethod
    def track_feedback_submitted(conversation, rating):
        return AnalyticsService.track_event('feedback_submitted', conversation=conversation, metadata={"rating": rating})

    @staticmethod
    def track_llm_call(conversation, model, latency_ms=None, error_code=None):
        return AnalyticsService.track_event(
            'llm_call',
            conversation=conversation,
            metadata={"model": model, "latency_ms": latency_ms, "error_code": error_code}
        )

    @staticmethod
    def track_lead_field_captured(lead, field_name):
        return AnalyticsService.track_event(
            'lead_field_captured',
            conversation=lead.conversation,
            lead=lead,
            metadata={"field": field_name}
        )

    @staticmethod
    def track_chat_error(conversation, error_code):
        return AnalyticsService.track_event('chat_error', conversation=conversation, metadata={"error_code": error_code})
