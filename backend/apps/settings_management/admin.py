from django.contrib import admin
from .models import Setting


@admin.register(Setting)
class SettingAdmin(admin.ModelAdmin):
    list_display = ('category', 'key', 'is_public', 'updated_at', 'updated_by')
    list_filter = ('category', 'is_public')
    search_fields = ('key', 'description')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('category', 'key')
