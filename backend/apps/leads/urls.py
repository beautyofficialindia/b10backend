from django.urls import path
from .views import DashboardSummaryAPIView, LeadListAPIView, LeadDetailAPIView

urlpatterns = [
    path('dashboard/', DashboardSummaryAPIView.as_view(), name='dashboard'),
    path('leads/', LeadListAPIView.as_view(), name='lead-list'),
    path('leads/<uuid:id>/', LeadDetailAPIView.as_view(), name='lead-detail'),
]
