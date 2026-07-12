from django.contrib import admin
from .models import LeadFollowUp, LeadActivity, LeadStatusHistory

@admin.register(LeadFollowUp)
class LeadFollowUpAdmin(admin.ModelAdmin):
    list_display = ('lead', 'followup_type', 'scheduled_at', 'status', 'created_at')
    list_filter = ('status', 'followup_type')
    search_fields = ('lead__company_name', 'notes')

@admin.register(LeadActivity)
class LeadActivityAdmin(admin.ModelAdmin):
    list_display = ('lead', 'activity_type', 'created_at')
    list_filter = ('activity_type',)

@admin.register(LeadStatusHistory)
class LeadStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ('lead', 'old_status', 'new_status', 'changed_at')
