from django.contrib import admin
from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['title', 'type', 'category', 'is_read', 'actor', 'created_at']
    list_filter = ['type', 'category', 'is_read']
    search_fields = ['title', 'message']
    readonly_fields = ['id', 'created_at', 'actor', 'recipient']
    ordering = ['-created_at']
    list_per_page = 50
    date_hierarchy = 'created_at'

    fieldsets = [
        ('Content', {'fields': ['id', 'title', 'message', 'type', 'category', 'action_url']}),
        ('State', {'fields': ['is_read']}),
        ('Ownership', {'fields': ['actor', 'recipient']}),
        ('Timestamps', {'fields': ['created_at']}),
    ]
