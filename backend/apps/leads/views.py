from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import ListAPIView, RetrieveUpdateAPIView, ListCreateAPIView, UpdateAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.filters import SearchFilter, OrderingFilter
from django.shortcuts import get_object_or_404
from .models import Lead, LeadNote
from .serializers import (
    LeadListSerializer, 
    LeadDetailSerializer, 
    LeadUpdateSerializer, 
    LeadNoteSerializer,
    LeadAssignmentSerializer
)
from apps.leads.services.lead_transition_service import LeadTransitionService
from apps.accounts.permissions import IsAdminUser, IsAdminOrSales, IsAdminSalesOrSupport


class LeadPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'

class LeadListAPIView(ListAPIView):
    permission_classes = [IsAdminSalesOrSupport]
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

    def get_permissions(self):
        if self.request.method in ['PATCH', 'PUT']:
            return [IsAdminOrSales()]
        return [IsAdminSalesOrSupport()]

    def get_serializer_class(self):
        if self.request.method in ['PATCH', 'PUT']:
            return LeadUpdateSerializer
        return LeadDetailSerializer
        
    def perform_update(self, serializer):
        old_status = self.get_object().status
        lead = serializer.save()
        if old_status != lead.status:
            # If manually set to 'qualified' via the API, ensure qualified_at is stamped
            # (QualificationService does this automatically for chatbot flows).
            if lead.status == 'qualified' and lead.qualified_at is None:
                from django.utils import timezone
                lead.qualified_at = timezone.now()
                lead.save(update_fields=['qualified_at'])
            LeadTransitionService.on_status_changed(lead, old_status, lead.status)

class LeadAssignmentAPIView(UpdateAPIView):
    permission_classes = [IsAdminOrSales]
    queryset = Lead.objects.all()
    serializer_class = LeadAssignmentSerializer
    lookup_field = 'id'
    
    def perform_update(self, serializer):
        lead = serializer.save()
        from apps.crm.models import LeadActivity
        
        assignee_id = lead.assigned_admin_id
        if assignee_id:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            try:
                assigned_user = User.objects.get(id=assignee_id)
                assigned_name = f"{assigned_user.first_name} {assigned_user.last_name}".strip() or assigned_user.email
                notes = f"Assigned to {assigned_name} by {self.request.user.email}"
            except User.DoesNotExist:
                notes = f"Assigned to a user by {self.request.user.email}"
                
            LeadActivity.objects.create(
                lead=lead,
                activity_type='assignment',
                notes=notes
            )
        else:
            LeadActivity.objects.create(
                lead=lead,
                activity_type='assignment',
                notes=f"Unassigned by {self.request.user.email}"
            )
        
class LeadNoteListCreateAPIView(ListCreateAPIView):
    permission_classes = [IsAdminOrSales]
    serializer_class = LeadNoteSerializer
    
    def get_queryset(self):
        return LeadNote.objects.filter(lead_id=self.kwargs['id'])
        
    def perform_create(self, serializer):
        lead = get_object_or_404(Lead, id=self.kwargs['id'])
        serializer.save(lead=lead, author_id=self.request.user.id)
