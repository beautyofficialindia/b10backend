from django.urls import path
from .views import (
    AdminSettingsListAPIView,
    AdminSettingsGroupsAPIView,
    AdminSettingsByGroupAPIView,
    AdminSettingDetailAPIView,
    InitializeSettingsAPIView,
    ResetSettingsAPIView,
    RefreshSettingsCacheAPIView,
    ClearSettingsCacheAPIView,
    AdminPlatformHealthAPIView
)

urlpatterns = [
    path('', AdminSettingsListAPIView.as_view(), name='settings-list'),
    path('groups/', AdminSettingsGroupsAPIView.as_view(), name='settings-groups'),
    path('detail/<uuid:id>/', AdminSettingDetailAPIView.as_view(), name='settings-detail'),
    path('initialize/', InitializeSettingsAPIView.as_view(), name='settings-initialize'),
    path('reset/', ResetSettingsAPIView.as_view(), name='settings-reset'),
    path('cache/refresh/', RefreshSettingsCacheAPIView.as_view(), name='settings-cache-refresh'),
    path('cache/clear/', ClearSettingsCacheAPIView.as_view(), name='settings-cache-clear'),
    path('health/', AdminPlatformHealthAPIView.as_view(), name='platform-health'),
    # This must be last to avoid catching 'groups', 'detail', etc.
    path('<str:group>/', AdminSettingsByGroupAPIView.as_view(), name='settings-by-group'),
]
