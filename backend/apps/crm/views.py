from rest_framework.views import APIView
from rest_framework.generics import ListCreateAPIView, ListAPIView, RetrieveUpdateAPIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from django.shortcuts import get_object_or_404
from apps.leads.models import Lead
from .models import LeadActivity, LeadStatusHistory, LeadFollowUp
from .serializers import (
    LeadActivitySerializer,
    LeadStatusHistorySerializer,
    LeadFollowUpSerializer,
    CRMDashboardSerializer
)
from .services.crm_service import CRMService
from apps.accounts.permissions import IsAdminUser, IsAdminOrSales

class CRMDashboardAPIView(APIView):
    permission_classes = [IsAdminUser]
    def get(self, request, *args, **kwargs):
        today = timezone.now().date()
        pending_followups = LeadFollowUp.objects.filter(status='pending').count()
        activities_today = LeadActivity.objects.filter(created_at__date=today).count()
        
        data = {
            "total_followups_pending": pending_followups,
            "total_activities_today": activities_today
        }
        serializer = CRMDashboardSerializer(data)
        return Response(serializer.data, status=status.HTTP_200_OK)

class LeadActivityListCreateAPIView(ListCreateAPIView):
    permission_classes = [IsAdminOrSales]
    serializer_class = LeadActivitySerializer

    def get_queryset(self):
        return LeadActivity.objects.filter(lead_id=self.kwargs['id'])

    def perform_create(self, serializer):
        lead = get_object_or_404(Lead, id=self.kwargs['id'])
        serializer.save(lead=lead)

class LeadStatusHistoryListAPIView(ListAPIView):
    permission_classes = [IsAdminOrSales]
    serializer_class = LeadStatusHistorySerializer

    def get_queryset(self):
        return LeadStatusHistory.objects.filter(lead_id=self.kwargs['id'])

class LeadFollowUpListCreateAPIView(ListCreateAPIView):
    permission_classes = [IsAdminOrSales]
    serializer_class = LeadFollowUpSerializer

    def get_queryset(self):
        return LeadFollowUp.objects.filter(lead_id=self.kwargs['id'])

    def perform_create(self, serializer):
        lead = get_object_or_404(Lead, id=self.kwargs['id'])
        followup = serializer.save(lead=lead)
        CRMService.log_activity(lead, 'followup_created', f"Follow-up scheduled for {followup.scheduled_at}")

class FollowUpDetailAPIView(RetrieveUpdateAPIView):
    permission_classes = [IsAdminOrSales]
    queryset = LeadFollowUp.objects.all()
    serializer_class = LeadFollowUpSerializer
    lookup_field = 'id'

    def perform_update(self, serializer):
        old_status = self.get_object().status
        followup = serializer.save()
        if old_status != followup.status and followup.status == 'completed':
            CRMService.log_activity(followup.lead, 'followup_completed', f"Follow-up completed: {followup.notes or ''}")
