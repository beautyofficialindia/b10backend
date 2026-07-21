from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, OpenApiExample

from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import ListAPIView, RetrieveUpdateAPIView, ListCreateAPIView, UpdateAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.throttling import AnonRateThrottle
from rest_framework.filters import SearchFilter, OrderingFilter
from django.shortcuts import get_object_or_404
from .models import Lead, LeadNote
from .serializers import (
    LeadListSerializer, 
    LeadDetailSerializer, 
    LeadUpdateSerializer, 
    LeadNoteSerializer,
    LeadAssignmentSerializer,
    PublicContactSerializer,
    PublicContactResponseSerializer
)
from apps.leads.services.lead_transition_service import LeadTransitionService
from apps.accounts.permissions import IsAdminUser, IsAdminOrSales, IsAdminSalesOrSupport


class LeadPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'

class PublicContactAPIView(APIView):
    authentication_classes = []
    permission_classes = []
    parser_classes = [MultiPartParser, FormParser]
    throttle_classes = [AnonRateThrottle]
    throttle_scope = 'contact_form'

    @extend_schema(
        summary="Submit Website Contact Form",
        description="""
Public endpoint used by the B10 website contact form.

Creates a Lead in the CRM with:
- Source: WEBSITE_CONTACT_FORM
- Status: gathering
- Lead Score: 0
- Conversation: null

No authentication is required.
        """,
        request=PublicContactSerializer,
        responses={201: PublicContactResponseSerializer},
        examples=[
            OpenApiExample(
                "Valid Submission",
                value={
                    "full_name": "John Doe",
                    "email": "john@example.com",
                    "phone_number": "9876543210",
                    "message": "I would like to discuss my project requirements.",
                    "attachment": "(binary)"
                }
            )
        ]
    )
    def post(self, request, *args, **kwargs):
        from .services.contact_form_service import ContactFormService

        
        serializer = PublicContactSerializer(data=request.data)
        if serializer.is_valid():
            try:
                ContactFormService.process_submission(serializer.validated_data)
                return Response(
                    {
                        "success": True,
                        "message": "Thank you for contacting B10. Our team will get back to you shortly."
                    },
                    status=status.HTTP_201_CREATED
                )
            except Exception:
                return Response(
                    {
                        "success": False,
                        "message": "Failed to upload attachment. Please try again."
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
        source_param = self.request.query_params.get('source')
        if status_param:
            queryset = queryset.filter(status=status_param)
        if source_param:
            queryset = queryset.filter(source=source_param)
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
