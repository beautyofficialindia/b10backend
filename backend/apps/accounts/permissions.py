from rest_framework import permissions

class IsAdminUser(permissions.IsAuthenticated):
    def has_permission(self, request, view):
        is_auth = super().has_permission(request, view)
        return is_auth and request.user.groups.filter(name='Admin').exists()

class IsSalesUser(permissions.IsAuthenticated):
    def has_permission(self, request, view):
        is_auth = super().has_permission(request, view)
        return is_auth and request.user.groups.filter(name='Sales').exists()

class IsSupportUser(permissions.IsAuthenticated):
    def has_permission(self, request, view):
        is_auth = super().has_permission(request, view)
        return is_auth and request.user.groups.filter(name='Support').exists()

class IsAdminOrSales(permissions.IsAuthenticated):
    def has_permission(self, request, view):
        is_auth = super().has_permission(request, view)
        return is_auth and request.user.groups.filter(name__in=['Admin', 'Sales']).exists()

class IsAdminSalesOrSupport(permissions.IsAuthenticated):
    def has_permission(self, request, view):
        is_auth = super().has_permission(request, view)
        return is_auth and request.user.groups.filter(name__in=['Admin', 'Sales', 'Support']).exists()
