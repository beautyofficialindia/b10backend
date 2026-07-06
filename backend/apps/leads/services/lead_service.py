from ..models import Lead, LeadEvent
from .lead_extractor import LeadExtractor
from apps.analytics.services.analytics_service import AnalyticsService

class LeadService:
    def __init__(self):
        self.extractor = LeadExtractor()

    def process_message_for_lead(self, conversation, message_text):
        extracted_data = self.extractor.extract(message_text)
        
        if not extracted_data:
            return None, False
            
        lead, created = Lead.objects.get_or_create(conversation=conversation)
        
        if created:
            from apps.crm.services.crm_service import CRMService
            CRMService.log_activity(lead, 'lead_created')
        
        updated = False
        updated_fields = []
        for field, value in extracted_data.items():
            current_value = getattr(lead, field)
            # Only update if current field is empty (never overwrite existing validated fields)
            if not current_value:
                setattr(lead, field, value)
                updated = True
                updated_fields.append(field)
                
        if updated:
            lead.save()
            for field in updated_fields:
                LeadEvent.objects.create(
                    lead=lead,
                    event_type='field_captured',
                    metadata={"field": field}
                )
                AnalyticsService.track_lead_field_captured(lead, field)
            
        return lead, created
