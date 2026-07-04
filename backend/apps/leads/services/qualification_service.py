class QualificationService:
    def __init__(self):
        # Email, industry, project_type, requirements
        self.required_fields = ['email', 'industry', 'project_type', 'requirements']

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
            CRMService.log_status_change(lead, old_status, 'qualified')
            CRMService.log_activity(lead, 'lead_qualified')
            
        return lead.status, missing_fields
