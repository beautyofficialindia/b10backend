from rest_framework import permissions


class _IsAdminGroupUser(permissions.IsAuthenticated):
    """Base: authenticated user who belongs to the Admin group or is a superuser."""

    def has_permission(self, request, view):
        is_auth = super().has_permission(request, view)
        return is_auth and (request.user.is_superuser or request.user.groups.filter(name='Admin').exists())


class CanViewNotification(_IsAdminGroupUser):
    """Permission: notifications.view_notification equivalent."""
    pass


class CanChangeNotification(_IsAdminGroupUser):
    """Permission: notifications.change_notification equivalent."""
    pass


class CanDeleteNotification(_IsAdminGroupUser):
    """Permission: notifications.delete_notification equivalent."""
    pass
