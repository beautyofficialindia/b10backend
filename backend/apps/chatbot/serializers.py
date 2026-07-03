from rest_framework import serializers

class ChatRequestSerializer(serializers.Serializer):
    session_id = serializers.UUIDField(required=False, allow_null=True)
    message = serializers.CharField(required=True, max_length=2000)
    metadata = serializers.JSONField(required=False, allow_null=True)
