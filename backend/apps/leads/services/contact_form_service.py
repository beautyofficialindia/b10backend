from django.db import transaction
from apps.leads.models import Lead, LeadAttachment
from common.services.cloudinary_service import CloudinaryUploadService
import logging

logger = logging.getLogger(__name__)

class ContactFormService:
    @staticmethod
    def process_submission(data):
        """
        Process a public contact form submission and create a Lead.
        No CRM, Notifications, or AI qualification is triggered here.
        """
        attachment_file = data.get('attachment')

        try:
            with transaction.atomic():
                lead = Lead.objects.create(
                    full_name=data['full_name'],
                    email=data['email'],
                    phone=data['phone_number'],
                    requirements=data['message'],
                    source=Lead.LeadSourceChoices.WEBSITE_CONTACT_FORM,
                    status='gathering',
                    lead_score=0,
                    conversation=None
                )

                if attachment_file:
                    folder = f"b10/website-leads/{lead.id}"
                    upload_resp = CloudinaryUploadService.upload_file(attachment_file, folder)
                    
                    LeadAttachment.objects.create(
                        lead=lead,
                        file_name=attachment_file.name,
                        file_url=upload_resp.get('secure_url', ''),
                        public_id=upload_resp.get('public_id', ''),
                        file_size=attachment_file.size,
                        mime_type=attachment_file.content_type,
                        is_public=False
                    )

                return lead
        except Exception as e:
            logger.error(f"Failed to process contact form submission: {e}")
            raise e

