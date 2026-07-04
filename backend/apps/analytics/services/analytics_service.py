from ..models import AnalyticsEvent

class AnalyticsService:
    @staticmethod
    def track_chat_started(conversation):
        AnalyticsEvent.objects.create(
            event_type='chat_started',
            conversation=conversation
        )

    @staticmethod
    def track_message_sent(conversation, role):
        AnalyticsEvent.objects.create(
            event_type='message_sent',
            conversation=conversation,
            metadata={"role": role}
        )

    @staticmethod
    def track_lead_created(lead):
        AnalyticsEvent.objects.create(
            event_type='lead_created',
            conversation=lead.conversation,
            lead=lead
        )

    @staticmethod
    def track_lead_qualified(lead):
        AnalyticsEvent.objects.create(
            event_type='lead_qualified',
            conversation=lead.conversation,
            lead=lead
        )

    @staticmethod
    def track_email_notification_sent(lead):
        AnalyticsEvent.objects.create(
            event_type='email_notification_sent',
            conversation=lead.conversation,
            lead=lead
        )

    @staticmethod
    def track_lead_converted(lead):
        AnalyticsEvent.objects.create(
            event_type='lead_converted',
            conversation=lead.conversation,
            lead=lead
        )

    @staticmethod
    def track_lead_lost(lead):
        AnalyticsEvent.objects.create(
            event_type='lead_lost',
            conversation=lead.conversation,
            lead=lead
        )
