from .prompt_builder import PromptBuilder
from .openrouter_client import OpenRouterClient
from ..models import ConversationSession, Message
from apps.leads.services.lead_service import LeadService
from apps.leads.services.qualification_service import QualificationService
from django.utils import timezone
import uuid

class ChatService:
    def __init__(self):
        self.prompt_builder = PromptBuilder()
        self.client = OpenRouterClient()
        self.lead_service = LeadService()
        self.qualification_service = QualificationService()

    def process_message(self, session_id, user_message):
        # 1. Get or create session
        session = None
        if session_id:
            try:
                session = ConversationSession.objects.get(session_id=session_id)
            except ConversationSession.DoesNotExist:
                pass
            except ValueError:
                pass

        if not session:
            session = ConversationSession.objects.create()

        # Update last_message_at
        session.last_message_at = timezone.now()
        session.save(update_fields=['last_message_at'])

        # 2. Upsert Lead and Recalculate Qualification
        lead = self.lead_service.process_message_for_lead(session, user_message)
        lead_status, missing_fields = self.qualification_service.calculate_status(lead)
        
        lead_summary = None
        if lead and lead_status == 'qualified':
            lead_summary = f"Email: {lead.email}, Industry: {lead.industry}, Type: {lead.project_type}"

        # 3. Get history (last 10 messages for context)
        history = list(session.messages.order_by('created_at')[:10])

        # 4. Build prompt messages (this now includes intent classification and lead injection)
        messages = self.prompt_builder.build_messages(
            history, 
            user_message,
            lead_status=lead_status,
            missing_fields=missing_fields,
            lead_summary=lead_summary
        )

        # 5. Save user message to DB
        Message.objects.create(session=session, role='user', content=user_message)

        # 6. Get LLM response
        try:
            bot_response = self.client.get_completion(messages)
        except Exception as e:
            bot_response = "I'm sorry, I'm currently experiencing technical difficulties. Please try again later."
            print(f"Error calling OpenRouter: {e}")

        # 7. Save bot message to DB
        Message.objects.create(session=session, role='assistant', content=bot_response)

        return {
            "session_id": str(session.session_id),
            "response": bot_response
        }
