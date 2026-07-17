from django.urls import path
from .views import (
    CRMDashboardAPIView,
    LeadActivityListCreateAPIView,
    LeadStatusHistoryListAPIView,
    LeadFollowUpListCreateAPIView,
    PendingFollowUpAPIView,
    FollowUpDetailAPIView
)

urlpatterns = [
    path('dashboard/', CRMDashboardAPIView.as_view(), name='crm-dashboard'),
    path('leads/<uuid:id>/activities/', LeadActivityListCreateAPIView.as_view(), name='lead-activities'),
    path('leads/<uuid:id>/status-history/', LeadStatusHistoryListAPIView.as_view(), name='lead-status-history'),
    path('leads/<uuid:id>/followups/', LeadFollowUpListCreateAPIView.as_view(), name='lead-followups'),
    path('followups/pending/', PendingFollowUpAPIView.as_view(), name='pending-followups'),
    path('followups/<uuid:id>/', FollowUpDetailAPIView.as_view(), name='followup-detail'),
]
