from django.contrib import admin
from .models import UserAuditLog


@admin.register(UserAuditLog)
class UserAuditLogAdmin(admin.ModelAdmin):
    list_display = ('action', 'actor', 'target_user', 'created_at')
    list_filter = ('action', 'created_at')
    search_fields = ('action', 'description')
    readonly_fields = ('actor', 'target_user', 'action', 'description', 'metadata', 'created_at')
    ordering = ('-created_at',)
