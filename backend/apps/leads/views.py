from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import ListAPIView, RetrieveUpdateAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import Lead
from .serializers import (
    LeadListSerializer, 
    LeadDetailSerializer, 
    LeadUpdateSerializer, 
    DashboardSummarySerializer
)
from apps.analytics.services.analytics_service import AnalyticsService
from apps.crm.services.crm_service import CRMService

class DashboardSummaryAPIView(APIView):
    def get(self, request, *args, **kwargs):
        leads = Lead.objects.all()
        summary = {
            "total_leads": leads.count(),
            "gathering": leads.filter(status="gathering").count(),
            "qualified": leads.filter(status="qualified").count(),
            "converted": leads.filter(status="converted").count(),
            "lost": leads.filter(status="lost").count(),
            "escalated": leads.filter(status="escalated").count(),
        }
        serializer = DashboardSummarySerializer(summary)
        return Response(serializer.data, status=status.HTTP_200_OK)

class LeadPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'

class LeadListAPIView(ListAPIView):
    queryset = Lead.objects.all()
    serializer_class = LeadListSerializer
    pagination_class = LeadPagination
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['full_name', 'company_name', 'email', 'phone', 'industry']
    ordering_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']

    def get_queryset(self):
        queryset = super().get_queryset()
        status_param = self.request.query_params.get('status')
        if status_param:
            queryset = queryset.filter(status=status_param)
        return queryset

class LeadDetailAPIView(RetrieveUpdateAPIView):
    queryset = Lead.objects.all()
    lookup_field = 'id'

    def get_serializer_class(self):
        if self.request.method in ['PATCH', 'PUT']:
            return LeadUpdateSerializer
        return LeadDetailSerializer
        
    def perform_update(self, serializer):
        old_status = self.get_object().status
        lead = serializer.save()
        if old_status != lead.status:
            CRMService.log_status_change(lead, old_status, lead.status)
            if lead.status == 'converted':
                AnalyticsService.track_lead_converted(lead)
            elif lead.status == 'lost':
                AnalyticsService.track_lead_lost(lead)
