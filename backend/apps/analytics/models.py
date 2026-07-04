from django.db import models
import uuid

class AnalyticsEvent(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conversation = models.ForeignKey('chatbot.ConversationSession', on_delete=models.SET_NULL, null=True, blank=True, related_name='events')
    lead = models.ForeignKey('leads.Lead', on_delete=models.SET_NULL, null=True, blank=True, related_name='events')
    
    EVENT_TYPES = [
        ('chat_started', 'Chat Started'),
        ('message_sent', 'Message Sent'),
        ('lead_created', 'Lead Created'),
        ('lead_qualified', 'Lead Qualified'),
        ('lead_converted', 'Lead Converted'),
        ('lead_lost', 'Lead Lost'),
        ('email_notification_sent', 'Email Notification Sent'),
    ]
    event_type = models.CharField(max_length=50, choices=EVENT_TYPES)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.event_type} - {self.created_at}"
