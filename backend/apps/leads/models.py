from django.db import models
import uuid

class Lead(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conversation = models.OneToOneField('chatbot.ConversationSession', on_delete=models.CASCADE, related_name='lead')
    
    full_name = models.CharField(max_length=255, null=True, blank=True)
    company_name = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    phone = models.CharField(max_length=50, null=True, blank=True)
    industry = models.CharField(max_length=255, null=True, blank=True)
    project_type = models.CharField(max_length=255, null=True, blank=True)
    budget_range = models.CharField(max_length=100, null=True, blank=True)
    timeline = models.CharField(max_length=100, null=True, blank=True)
    requirements = models.TextField(null=True, blank=True)
    
    STATUS_CHOICES = [
        ('gathering', 'Gathering'),
        ('qualified', 'Qualified'),
        ('disqualified', 'Disqualified'),
        ('escalated', 'Escalated'),
        ('converted', 'Converted'),
        ('lost', 'Lost'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='gathering')
    notification_sent = models.BooleanField(default=False)
    source = models.CharField(max_length=50, default='chatbot')
    lead_score = models.PositiveIntegerField(default=0)
    assigned_admin_id = models.UUIDField(null=True, blank=True)
    external_crm_id = models.CharField(max_length=255, null=True, blank=True)
    external_crm_provider = models.CharField(max_length=100, null=True, blank=True)
    crm_synced_at = models.DateTimeField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    # Qualification & CRM lifecycle timestamps
    qualified_at = models.DateTimeField(null=True, blank=True)
    last_contacted_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Lead: {self.full_name or self.email or 'Anonymous'} ({self.status})"


class LeadNote(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name='notes')
    author_id = models.UUIDField(null=True, blank=True)
    note = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']


class LeadEvent(models.Model):
    EVENT_TYPES = [
        ('field_captured', 'Field Captured'),
        ('status_changed', 'Status Changed'),
        ('notification_sent', 'Notification Sent'),
        ('escalation_triggered', 'Escalation Triggered'),
        ('lead_qualified', 'Lead Qualified'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name='lead_events')
    event_type = models.CharField(max_length=50, choices=EVENT_TYPES)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
