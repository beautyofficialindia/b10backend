from rest_framework import serializers
from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    actor_name = serializers.SerializerMethodField()
    recipient_name = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = [
            'id',
            'title',
            'message',
            'type',
            'category',
            'action_url',
            'is_read',
            'actor',
            'actor_name',
            'recipient',
            'recipient_name',
            'created_at',
        ]
        # All fields are read-only; mutations go through dedicated endpoints only
        read_only_fields = fields

    def get_actor_name(self, obj):
        if not obj.actor:
            return None
        user = obj.actor
        name = f"{getattr(user, 'first_name', '')} {getattr(user, 'last_name', '')}".strip()
        return name or getattr(user, 'email', str(user))

    def get_recipient_name(self, obj):
        if not obj.recipient:
            return None
        user = obj.recipient
        name = f"{getattr(user, 'first_name', '')} {getattr(user, 'last_name', '')}".strip()
        return name or getattr(user, 'email', str(user))
