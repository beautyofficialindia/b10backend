from rest_framework import serializers
from .models import Feedback

class ChatRequestSerializer(serializers.Serializer):
    session_id = serializers.UUIDField(
        required=False, 
        allow_null=True,
        error_messages={
            'invalid': "Provide a session_id returned by a previous chat response or omit this field to start a new conversation."
        }
    )
    message = serializers.CharField(required=True, max_length=2000)
    metadata = serializers.JSONField(required=False, allow_null=True)

class ChatResponseSerializer(serializers.Serializer):
    session_id = serializers.UUIDField()
    response = serializers.CharField()


class ChatSessionCreateRequestSerializer(serializers.Serializer):
    source_channel = serializers.CharField(required=False, default="website_widget", max_length=50)

    def validate_source_channel(self, value):
        allowed = {"website_widget", "web_widget", "api"}
        return value if value in allowed else "website_widget"


class ChatSessionCreateResponseSerializer(serializers.Serializer):
    session_id = serializers.UUIDField()
    session_token = serializers.CharField()
    expires_at = serializers.DateTimeField(allow_null=True)


class FeedbackCreateSerializer(serializers.ModelSerializer):
    session_id = serializers.UUIDField(write_only=True)
    message_id = serializers.IntegerField(required=False, allow_null=True, write_only=True)

    class Meta:
        model = Feedback
        fields = ['session_id', 'message_id', 'rating', 'comment']
