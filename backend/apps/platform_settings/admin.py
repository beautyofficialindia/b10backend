from django.contrib import admin
from .models import PlatformSetting
from .constants import ValueType

@admin.register(PlatformSetting)
class PlatformSettingAdmin(admin.ModelAdmin):
    list_display = (
        'group', 
        'key', 
        'display_name',
        'get_masked_value', 
        'value_type', 
        'is_editable', 
        'is_public', 
        'is_sensitive',
        'display_order',
        'updated_by'
    )
    list_filter = (
        'group', 
        'is_editable', 
        'is_public', 
        'is_sensitive', 
        'value_type'
    )
    search_fields = ('key', 'description', 'value', 'display_name')
    readonly_fields = ('created_at', 'updated_at', 'id')
    ordering = ('group', 'display_order', 'key')
    
    fieldsets = (
        ('Basic Information', {
            'fields': (
                'id', 
                'group', 
                'key', 
                'display_name', 
                'description', 
                'display_order'
            )
        }),
        ('Value Configuration', {
            'fields': (
                'value', 
                'value_type', 
                'validation_rules'
            )
        }),
        ('Visibility & Permissions', {
            'fields': (
                'is_public', 
                'is_editable', 
                'is_sensitive'
            )
        }),
        ('Metadata', {
            'fields': (
                'updated_by', 
                'created_at', 
                'updated_at'
            ),
            'classes': ('collapse',)
        })
    )

    def get_masked_value(self, obj):
        if obj.is_sensitive and obj.value:
            return '*' * 12
        
        if len(obj.value) > 50:
            return f"{obj.value[:47]}..."
        return obj.value

    get_masked_value.short_description = 'Value'
    
    def save_model(self, request, obj, form, change):
        if not obj.updated_by:
            obj.updated_by = request.user
        super().save_model(request, obj, form, change)
