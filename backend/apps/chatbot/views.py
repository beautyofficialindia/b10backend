from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from django.core import signing
from django.utils import timezone
from datetime import timedelta
from drf_spectacular.utils import extend_schema, OpenApiExample
from common.responses import success_response, error_response
from .serializers import (
    ChatRequestSerializer,
    ChatResponseSerializer,
    ChatSessionCreateRequestSerializer,
    FeedbackCreateSerializer,
)
from .models import ConversationSession, Message, Feedback
from .services.chat_service import ChatService
from .services.knowledge_provider import KnowledgeProviderFactory
from apps.analytics.services.analytics_service import AnalyticsService


def _session_token(session):
    return signing.dumps({"session_id": str(session.session_id)}, salt="chat-session")

class ChatAPIView(APIView):
    throttle_classes = [AnonRateThrottle, UserRateThrottle]

    @extend_schema(
        request=ChatRequestSerializer,
        responses={200: ChatResponseSerializer},
        examples=[
            OpenApiExample(
                'Start New Conversation',
                description='Starts a new conversation.',
                value={
                    "message": "What services does B10 IT Solution provide?"
                },
                request_only=True,
            ),
            OpenApiExample(
                'Continue Conversation',
                description='Continues an existing conversation.',
                value={
                    "message": "Tell me more about your AI services.",
                    "session_id": "<session-id-returned-from-previous-response>"
                },
                request_only=True,
            )
        ]
    )
    def post(self, request, *args, **kwargs):
        serializer = ChatRequestSerializer(data=request.data)
        
        if serializer.is_valid():
            session_id = serializer.validated_data.get('session_id')
            message = serializer.validated_data.get('message')
            metadata = serializer.validated_data.get('metadata') # passed to chat_service if needed in future

            chat_service = ChatService()
            result = chat_service.process_message(session_id, message)

            return Response(result, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ChatSessionCreateAPIView(APIView):
    authentication_classes = []
    permission_classes = []
    throttle_classes = [AnonRateThrottle]

    @extend_schema(request=ChatSessionCreateRequestSerializer)
    def post(self, request, *args, **kwargs):
        serializer = ChatSessionCreateRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        channel = serializer.validated_data.get('source_channel')
        if channel == 'website_widget':
            channel = 'web_widget'
        session = ConversationSession.objects.create(channel=channel)
        AnalyticsService.track_chat_started(session)
        expires_at = timezone.now() + timedelta(hours=1)
        return success_response(
            data={
                "session_id": str(session.session_id),
                "session_token": _session_token(session),
                "expires_at": expires_at,
            },
            message="Session created",
            status=status.HTTP_201_CREATED,
        )


class FeedbackAPIView(APIView):
    authentication_classes = []
    permission_classes = []
    throttle_classes = [AnonRateThrottle]

    @extend_schema(request=FeedbackCreateSerializer)
    def post(self, request, *args, **kwargs):
        serializer = FeedbackCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        session_id = serializer.validated_data['session_id']
        message_id = serializer.validated_data.get('message_id')
        try:
            session = ConversationSession.objects.get(session_id=session_id)
        except ConversationSession.DoesNotExist:
            return error_response("NOT_FOUND_RESOURCE", "Conversation session was not found.", status=status.HTTP_404_NOT_FOUND)

        message = None
        if message_id:
            try:
                message = Message.objects.get(id=message_id, session=session)
            except Message.DoesNotExist:
                return error_response("NOT_FOUND_RESOURCE", "Message was not found for this session.", status=status.HTTP_404_NOT_FOUND)

        feedback = Feedback.objects.create(
            session=session,
            message=message,
            rating=serializer.validated_data['rating'],
            comment=serializer.validated_data.get('comment'),
        )
        return success_response(
            data={"feedback_id": str(feedback.id)},
            message="Feedback submitted",
            status=status.HTTP_201_CREATED,
        )


class CompanyAPIView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, *args, **kwargs):
        data = KnowledgeProviderFactory.get_provider().get_category_data('company') or {}
        return success_response(data=data)


class ServicesAPIView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, *args, **kwargs):
        services = KnowledgeProviderFactory.get_provider().get_category_data('services') or []
        industry = request.query_params.get('industry')
        if industry:
            services = [
                service for service in services
                if industry.lower() in [str(item).lower() for item in service.get('related_industries', [])]
                or industry.lower() in str(service).lower()
            ]
        return success_response(data=services)


class ServiceDetailAPIView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, slug, *args, **kwargs):
        services = KnowledgeProviderFactory.get_provider().get_category_data('services') or []
        for service in services:
            identifiers = {service.get('id'), service.get('slug'), str(service.get('name', '')).lower().replace(' ', '-')}
            if slug in identifiers:
                return success_response(data=service)
        return error_response("NOT_FOUND_RESOURCE", "No service found for the given identifier.", {"slug": slug}, status=status.HTTP_404_NOT_FOUND)


class FAQAPIView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, *args, **kwargs):
        return success_response(data=KnowledgeProviderFactory.get_provider().get_category_data('faq') or [])


class HealthAPIView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, *args, **kwargs):
        return success_response(data={"status": "ok"}, meta={"version": "v1"})
