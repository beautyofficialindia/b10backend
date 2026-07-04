from django.core.mail import send_mail
from django.conf import settings
from apps.analytics.services.analytics_service import AnalyticsService

class NotificationService:
    def send_lead_notification(self, lead):
        subject = f"New Qualified Lead: {lead.project_type} for {lead.industry}"
        
        message = f"""
A new lead has been qualified by the AI Assistant.

--- Lead Details ---
Full Name: {lead.full_name or 'N/A'}
Company Name: {lead.company_name or 'N/A'}
Email: {lead.email or 'N/A'}
Phone: {lead.phone or 'N/A'}
Industry: {lead.industry or 'N/A'}
Project Type: {lead.project_type or 'N/A'}
Budget: {lead.budget_range or 'N/A'}
Timeline: {lead.timeline or 'N/A'}
Requirements:
{lead.requirements or 'N/A'}
--------------------
"""
        
        # Send email (currently uses console backend as configured in settings.py)
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=['sales@b10itsolution.com'],
            fail_silently=False,
        )
        AnalyticsService.track_email_notification_sent(lead)
