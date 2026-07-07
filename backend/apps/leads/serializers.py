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
        fields = ['status']
        
    def validate_status(self, value):
        allowed_statuses = ['gathering', 'qualified', 'converted', 'lost', 'escalated']
        if value not in allowed_statuses:
            raise serializers.ValidationError("Invalid status update.")
        return value

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
