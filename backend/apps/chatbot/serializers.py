from rest_framework import serializers

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
