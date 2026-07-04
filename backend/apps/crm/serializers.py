from rest_framework import serializers
from .models import LeadActivity, LeadStatusHistory, LeadFollowUp

class LeadActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = LeadActivity
        fields = '__all__'
        read_only_fields = ['lead', 'created_at']

class LeadStatusHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = LeadStatusHistory
        fields = '__all__'

class LeadFollowUpSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeadFollowUp
        fields = '__all__'
        read_only_fields = ['lead', 'created_at', 'updated_at']

class CRMDashboardSerializer(serializers.Serializer):
    total_followups_pending = serializers.IntegerField()
    total_activities_today = serializers.IntegerField()
