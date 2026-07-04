from django.test import TestCase
from .models import ConversationSession, Message

class ChatbotTests(TestCase):
    def test_chat_creation(self):
        session = ConversationSession.objects.create()
        self.assertIsNotNone(session.session_id)
        msg = Message.objects.create(session=session, role='user', content='Hello')
        self.assertEqual(msg.content, 'Hello')
