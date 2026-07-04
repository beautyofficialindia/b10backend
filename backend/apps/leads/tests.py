from django.test import TestCase
from apps.chatbot.models import ConversationSession
from apps.leads.models import Lead
from apps.leads.services.qualification_service import QualificationService

class QualificationTests(TestCase):
    def setUp(self):
        self.session = ConversationSession.objects.create()
        self.lead = Lead.objects.create(conversation=self.session)
        self.qual_service = QualificationService()

    def test_missing_fields(self):
        status, missing = self.qual_service.calculate_status(self.lead)
        self.assertEqual(status, 'gathering')
        self.assertIn('email', missing)

    def test_qualified(self):
        self.lead.email = 'test@test.com'
        self.lead.industry = 'Tech'
        self.lead.project_type = 'Web'
        self.lead.requirements = 'Build a site'
        self.lead.save()
        status, missing = self.qual_service.calculate_status(self.lead)
        self.assertEqual(status, 'qualified')
        self.assertEqual(len(missing), 0)
