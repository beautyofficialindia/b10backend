from .prompt_builder import PromptBuilder
from .openrouter_client import OpenRouterClient
from .scope_guard import ScopeGuard
from .escalation_service import EscalationService
from .response_validator import ResponseValidator
from ..models import ConversationSession, Message
from apps.leads.services.lead_service import LeadService
from apps.leads.services.qualification_service import QualificationService
from apps.leads.services.notification_service import NotificationService
from apps.analytics.services.analytics_service import AnalyticsService
from django.utils import timezone
import uuid
import logging

logger = logging.getLogger(__name__)

class ChatService:
    def __init__(self):
        self.prompt_builder = PromptBuilder()
        self.client = OpenRouterClient()
        self.scope_guard = ScopeGuard()
        self.escalation_service = EscalationService()
        self.response_validator = ResponseValidator()
        self.lead_service = LeadService()
        self.qualification_service = QualificationService()
        self.notification_service = NotificationService()

    def process_message(self, session_id, user_message):
        # 1. Get or create session
        session = None
        session_created = False
        if session_id:
            try:
                session = ConversationSession.objects.get(session_id=session_id)
            except ConversationSession.DoesNotExist:
                pass
            except ValueError:
                pass

        if not session:
            session = ConversationSession.objects.create()
            session_created = True

        if session_created:
            AnalyticsService.track_chat_started(session)

        # Update last_message_at
        session.last_message_at = timezone.now()
        session.save(update_fields=['last_message_at'])

        AnalyticsService.track_message_sent(session, "user")

        scope_decision = self.scope_guard.classify(user_message)
        should_escalate, escalation_reason = self.escalation_service.should_escalate(user_message, scope_decision, session)

        if not scope_decision.allowed:
            metadata = session.metadata or {}
            metadata["off_topic_count"] = metadata.get("off_topic_count", 0) + 1
            session.metadata = metadata
            session.save(update_fields=["metadata", "updated_at"])

            self._create_message(session, 'user', user_message)
            if should_escalate:
                self.escalation_service.mark_escalated(session, escalation_reason)
                bot_response = self.escalation_service.message()
                AnalyticsService.track_escalation(session, escalation_reason)
            else:
                bot_response = self.scope_guard.refusal_message(scope_decision.reason)
                AnalyticsService.track_scope_refusal(session, scope_decision.reason)

            self._create_message(
                session,
                'assistant',
                bot_response,
                response_metadata={
                    "mode": "refusal",
                    "scope_reason": scope_decision.reason,
                    "risk_level": scope_decision.risk_level,
                }
            )
            AnalyticsService.track_message_sent(session, "assistant")
            return {
                "session_id": str(session.session_id),
                "response": bot_response
            }

        # 2. Upsert Lead and Recalculate Qualification
        lead, lead_created = self.lead_service.process_message_for_lead(session, user_message)
        if lead_created:
            AnalyticsService.track_lead_created(lead)

        lead_status, missing_fields = self.qualification_service.calculate_status(lead)
        self._sync_session_qualification_state(session, lead_status)
        
        lead_summary = None
        if lead and lead_status == 'qualified':
            lead_summary = (
                f"Name: {lead.full_name}, Company: {lead.company_name}, Email: {lead.email}, "
                f"Industry: {lead.industry}, Type: {lead.project_type}"
            )
            
            # If it just became qualified
            if not lead.notification_sent:
                AnalyticsService.track_lead_qualified(lead)
                sent = self.notification_service.send_lead_notification(lead)
                if sent:
                    lead.notification_sent = True
                    lead.save(update_fields=['notification_sent'])

        if should_escalate:
            self.escalation_service.mark_escalated(session, escalation_reason)
            if lead:
                AnalyticsService.track_escalation(session, escalation_reason, lead=lead)
            bot_response = self.escalation_service.message()
            self._create_message(session, 'user', user_message)
            self._create_message(
                session,
                'assistant',
                bot_response,
                response_metadata={
                    "mode": "human_escalation",
                    "escalation_reason": escalation_reason,
                }
            )
            AnalyticsService.track_message_sent(session, "assistant")
            return {
                "session_id": str(session.session_id),
                "response": bot_response
            }

        # 3. Get history (last 10 messages for context)
        history = list(session.messages.order_by('-created_at')[:10])
        history.reverse()

        # 4. Build prompt messages (this now includes intent classification and lead injection)
        messages = self.prompt_builder.build_messages(
            history, 
            user_message,
            lead_status=lead_status,
            missing_fields=missing_fields,
            lead_summary=lead_summary
        )

        # 5. Save user message to DB
        self._create_message(session, 'user', user_message)

        # 6. Get LLM response
        ai_response = None
        error_code = None
        try:
            ai_response = self.client.generate_response(messages)
            bot_response = ai_response.content
            AnalyticsService.track_llm_call(session, ai_response.model, ai_response.latency_ms)
        except Exception as e:
            error_code = e.__class__.__name__
            bot_response = "I'm sorry, I'm currently experiencing technical difficulties. Please contact B10 IT Solution directly or try again later."
            AnalyticsService.track_chat_error(session, error_code)
            AnalyticsService.track_llm_call(session, "openrouter", error_code=error_code)
            logger.error("Error calling OpenRouter: %s", e)

        valid_response, validation_reason = self.response_validator.validate(bot_response)
        post_decision = self.scope_guard.validate_response(bot_response, scope_decision)
        if not valid_response or not post_decision.allowed:
            bot_response = self.response_validator.fallback_message()
            error_code = validation_reason if not valid_response else post_decision.reason

        # 7. Save bot message to DB
        self._create_message(
            session,
            'assistant',
            bot_response,
            response_metadata={
                "mode": scope_decision.mode,
                "scope_reason": scope_decision.reason,
                "response_validation": validation_reason,
                "error_code": error_code,
                "escalation_reason": escalation_reason,
            },
            token_count_input=ai_response.token_count_input if ai_response else None,
            token_count_output=ai_response.token_count_output if ai_response else None,
            processing_time_ms=ai_response.latency_ms if ai_response else None,
            error_code=error_code,
        )
        AnalyticsService.track_message_sent(session, "assistant")

        return {
            "session_id": str(session.session_id),
            "response": bot_response
        }

    def _create_message(self, session, role, content, **kwargs):
        last_message = session.messages.order_by('-sequence_number').first()
        next_sequence = ((last_message.sequence_number or 0) if last_message else 0) + 1
        return Message.objects.create(
            session=session,
            role=role,
            content=content,
            sequence_number=next_sequence,
            **kwargs
        )

    def _sync_session_qualification_state(self, session, lead_status):
        if not lead_status:
            return
        if lead_status == 'qualified':
            session.qualification_state = 'qualified'
        elif lead_status == 'gathering':
            session.qualification_state = 'gathering'
        elif lead_status == 'escalated':
            session.qualification_state = 'escalated_to_human'
        else:
            session.qualification_state = 'disqualified'
        session.save(update_fields=['qualification_state', 'updated_at'])
