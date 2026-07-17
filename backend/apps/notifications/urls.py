from django.urls import path
from .views import (
    NotificationListView,
    NotificationDetailView,
    NotificationMarkReadView,
    NotificationMarkUnreadView,
    NotificationMarkAllReadView,
    NotificationDeleteReadView,
    NotificationUnreadCountView,
)

# IMPORTANT: static string routes must be registered BEFORE <uuid:id> routes
# to prevent Django from treating 'read-all', 'read', 'unread-count' as UUID params.
urlpatterns = [
    path('', NotificationListView.as_view(), name='notification-list'),
    path('unread-count/', NotificationUnreadCountView.as_view(), name='notification-unread-count'),
    path('read-all/', NotificationMarkAllReadView.as_view(), name='notification-mark-all-read'),
    path('read/', NotificationDeleteReadView.as_view(), name='notification-delete-read'),
    # Per-notification routes (UUID) — must come after all static routes
    path('<uuid:id>/', NotificationDetailView.as_view(), name='notification-detail'),
    path('<uuid:id>/read/', NotificationMarkReadView.as_view(), name='notification-mark-read'),
    path('<uuid:id>/unread/', NotificationMarkUnreadView.as_view(), name='notification-mark-unread'),
]
