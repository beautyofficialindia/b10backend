from django.urls import path

from .views import PublicSettingsView, SettingsAdminViewSet

admin_view = SettingsAdminViewSet.as_view({
    'get': 'list',
})
category_view = SettingsAdminViewSet.as_view({
    'get': 'retrieve_category',
    'patch': 'update_category',
})

urlpatterns = [
    path('', admin_view, name='settings-list'),
    path('public/', PublicSettingsView.as_view(), name='settings-public'),
    path('<str:category>/', category_view, name='settings-category'),
]
