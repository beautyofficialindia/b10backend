from django.urls import path
from .views import (
    DashboardSummaryAPIView, 
    LeadListAPIView, 
    LeadDetailAPIView,
    LeadAssignmentAPIView,
    LeadNoteListCreateAPIView
)

urlpatterns = [
    path('dashboard/', DashboardSummaryAPIView.as_view(), name='dashboard'),
    path('leads/', LeadListAPIView.as_view(), name='lead-list'),
    path('leads/<uuid:id>/', LeadDetailAPIView.as_view(), name='lead-detail'),
    path('leads/<uuid:id>/assign/', LeadAssignmentAPIView.as_view(), name='lead-assign'),
    path('leads/<uuid:id>/notes/', LeadNoteListCreateAPIView.as_view(), name='lead-notes'),
]
