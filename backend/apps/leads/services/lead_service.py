from ..models import Lead
from .lead_extractor import LeadExtractor

class LeadService:
    def __init__(self):
        self.extractor = LeadExtractor()

    def process_message_for_lead(self, conversation, message_text):
        extracted_data = self.extractor.extract(message_text)
        
        if not extracted_data:
            return None, False
            
        lead, created = Lead.objects.get_or_create(conversation=conversation)
        
        updated = False
        for field, value in extracted_data.items():
            current_value = getattr(lead, field)
            # Only update if current field is empty (never overwrite existing validated fields)
            if not current_value:
                setattr(lead, field, value)
                updated = True
                
        if updated:
            lead.save()
            
        return lead, created
