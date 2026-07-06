class QualificationService:
    def __init__(self):
        self.required_fields = ['full_name', 'company_name', 'email', 'industry', 'project_type', 'requirements']

    def calculate_status(self, lead):
        if not lead:
            return None, self.required_fields
            
        missing_fields = []
        for field in self.required_fields:
            if not getattr(lead, field):
                missing_fields.append(field)
                
        if not missing_fields and lead.status == 'gathering':
            old_status = lead.status
            lead.status = 'qualified'
            lead.save(update_fields=['status'])
            
            from apps.crm.services.crm_service import CRMService
            from apps.leads.models import LeadEvent
            CRMService.log_status_change(lead, old_status, 'qualified')
            CRMService.log_activity(lead, 'lead_qualified')
            LeadEvent.objects.create(
                lead=lead,
                event_type='lead_qualified',
                metadata={"old_status": old_status, "new_status": "qualified"}
            )
            
        return lead.status, missing_fields
