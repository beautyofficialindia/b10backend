from django.urls import path
from .views import AnalyticsDashboardAPIView, AnalyticsTimelineAPIView, AnalyticsFunnelAPIView

urlpatterns = [
    path('', AnalyticsDashboardAPIView.as_view(), name='analytics-dashboard'),
    path('timeline/', AnalyticsTimelineAPIView.as_view(), name='analytics-timeline'),
    path('funnel/', AnalyticsFunnelAPIView.as_view(), name='analytics-funnel'),
]
