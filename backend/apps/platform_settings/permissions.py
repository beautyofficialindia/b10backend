from rest_framework import permissions

class CanViewPlatformSettings(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.has_perm('platform_settings.can_view_settings')

class CanChangePlatformSettings(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.has_perm('platform_settings.can_change_settings')

class CanInitializePlatformSettings(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.has_perm('platform_settings.can_initialize_settings')
