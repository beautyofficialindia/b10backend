from django.urls import path
from .views import (
    AnalyticsOverviewAPIView,
    AnalyticsLeadsAPIView,
    AnalyticsCRMAPIView,
    AnalyticsChatAPIView,
    AnalyticsKnowledgeAPIView,
    AnalyticsUsersAPIView,
    AnalyticsExportAPIView,
)

urlpatterns = [
    path('overview/', AnalyticsOverviewAPIView.as_view(), name='analytics-overview'),
    path('leads/', AnalyticsLeadsAPIView.as_view(), name='analytics-leads'),
    path('crm/', AnalyticsCRMAPIView.as_view(), name='analytics-crm'),
    path('chat/', AnalyticsChatAPIView.as_view(), name='analytics-chat'),
    path('knowledge/', AnalyticsKnowledgeAPIView.as_view(), name='analytics-knowledge'),
    path('users/', AnalyticsUsersAPIView.as_view(), name='analytics-users'),
    path('export/', AnalyticsExportAPIView.as_view(), name='analytics-export'),
]
