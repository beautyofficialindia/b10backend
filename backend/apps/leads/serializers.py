from rest_framework import serializers
from .models import Lead
from apps.chatbot.models import ConversationSession, Message

class DashboardSummarySerializer(serializers.Serializer):
    total_leads = serializers.IntegerField()
    gathering = serializers.IntegerField()
    qualified = serializers.IntegerField()
    converted = serializers.IntegerField()
    lost = serializers.IntegerField()
    escalated = serializers.IntegerField()

class LeadListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lead
        fields = ['id', 'full_name', 'company_name', 'email', 'phone', 'industry', 'project_type', 'status', 'created_at']

class LeadUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lead
        fields = ['status', 'priority']
        
    def validate_status(self, value):
        allowed_statuses = ['gathering', 'qualified', 'disqualified', 'converted', 'lost', 'escalated']
        if value not in allowed_statuses:
            raise serializers.ValidationError("Invalid status update.")
        return value

    def validate_priority(self, value):
        allowed_priorities = ['low', 'medium', 'high', 'urgent']
        if value not in allowed_priorities:
            raise serializers.ValidationError("Invalid priority update.")
        return value

class LeadAssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lead
        fields = ['assigned_admin_id']

from .models import LeadNote

from django.contrib.auth import get_user_model

class LeadNoteSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()

    class Meta:
        model = LeadNote
        fields = '__all__'
        read_only_fields = ['id', 'created_at']

    def get_author(self, obj):
        if not obj.author_id:
            return None
        User = get_user_model()
        try:
            user = User.objects.get(id=obj.author_id)
            return {
                "id": user.id,
                "username": getattr(user, 'username', getattr(user, 'email', '')),
                "full_name": getattr(user, 'full_name', f"{getattr(user, 'first_name', '')} {getattr(user, 'last_name', '')}".strip())
            }
        except User.DoesNotExist:
            return None

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['role', 'content', 'created_at']

class ConversationSessionSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True, read_only=True)
    
    class Meta:
        model = ConversationSession
        fields = ['session_id', 'is_active', 'created_at', 'last_message_at', 'messages']

class LeadDetailSerializer(serializers.ModelSerializer):
    conversation = ConversationSessionSerializer(read_only=True)
    
    class Meta:
        model = Lead
        fields = '__all__'
