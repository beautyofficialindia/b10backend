from django.contrib import admin
from .models import Lead, LeadNote, LeadEvent


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = [
        'full_name', 'company_name', 'email', 'phone',
        'status', 'source', 'lead_score',
        'qualified_at', 'last_contacted_at', 'created_at',
    ]
    list_filter = ['status', 'source', 'industry', 'project_type']
    search_fields = ['full_name', 'company_name', 'email', 'phone']
    readonly_fields = ['id', 'created_at', 'updated_at', 'qualified_at', 'notification_sent']
    ordering = ['-created_at']

    def save_model(self, request, obj, form, change):
        """
        Routes status transitions through LeadTransitionService — the same
        orchestrator used by the REST API. This ensures Admin qualification
        triggers notifications, analytics, and CRM logs identically to API qualification.
        """
        old_status = None
        if change and 'status' in form.changed_data:
            old_status = Lead.objects.get(pk=obj.pk).status

        super().save_model(request, obj, form, change)

        if old_status and old_status != obj.status:
            # Stamp qualified_at for Admin-driven qualification (write-once)
            if obj.status == 'qualified' and obj.qualified_at is None:
                from django.utils import timezone
                Lead.objects.filter(pk=obj.pk).update(qualified_at=timezone.now())
                obj.refresh_from_db(fields=['qualified_at'])
            from apps.leads.services.lead_transition_service import LeadTransitionService
            LeadTransitionService.on_status_changed(obj, old_status, obj.status)


@admin.register(LeadNote)
class LeadNoteAdmin(admin.ModelAdmin):
    list_display = ['lead', 'author_id', 'created_at']
    readonly_fields = ['created_at']
    ordering = ['-created_at']


@admin.register(LeadEvent)
class LeadEventAdmin(admin.ModelAdmin):
    list_display = ['lead', 'event_type', 'created_at']
    list_filter = ['event_type']
    readonly_fields = ['id', 'created_at']
    ordering = ['-created_at']
