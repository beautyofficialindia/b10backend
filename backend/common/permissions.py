from rest_framework import permissions


class IsReadOnlySupport(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            bool(request.user and request.user.is_authenticated)
            and request.method in permissions.SAFE_METHODS
            and request.user.groups.filter(name="Support").exists()
        )


class CanViewPII(permissions.BasePermission):
    allowed_groups = ("Admin", "Sales")

    def has_permission(self, request, view):
        return (
            bool(request.user and request.user.is_authenticated)
            and request.user.groups.filter(name__in=self.allowed_groups).exists()
        )


class CanManageCRM(permissions.BasePermission):
    allowed_groups = ("Admin", "Sales")

    def has_permission(self, request, view):
        return (
            bool(request.user and request.user.is_authenticated)
            and request.user.groups.filter(name__in=self.allowed_groups).exists()
        )


class CanViewAnalytics(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            bool(request.user and request.user.is_authenticated)
            and request.user.groups.filter(name="Admin").exists()
        )
