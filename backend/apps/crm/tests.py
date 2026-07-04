from django.test import TestCase
from apps.chatbot.models import ConversationSession
from apps.leads.models import Lead
from apps.crm.models import LeadActivity
from apps.crm.services.crm_service import CRMService

class CRMTests(TestCase):
    def setUp(self):
        self.session = ConversationSession.objects.create()
        self.lead = Lead.objects.create(conversation=self.session)

    def test_log_activity(self):
        CRMService.log_activity(self.lead, 'note_added', 'Test Note')
        self.assertEqual(LeadActivity.objects.count(), 1)
        activity = LeadActivity.objects.first()
        self.assertEqual(activity.activity_type, 'note_added')
        self.assertEqual(activity.notes, 'Test Note')
