from django.test import TestCase
from apps.chatbot.models import ConversationSession
from apps.analytics.models import AnalyticsEvent
from apps.analytics.services.analytics_service import AnalyticsService

class AnalyticsTests(TestCase):
    def setUp(self):
        self.session = ConversationSession.objects.create()

    def test_track_chat_started(self):
        AnalyticsService.track_chat_started(self.session)
        self.assertEqual(AnalyticsEvent.objects.count(), 1)
        event = AnalyticsEvent.objects.first()
        self.assertEqual(event.event_type, 'chat_started')
