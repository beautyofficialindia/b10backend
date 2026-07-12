from django.db import models
import uuid

class LeadActivity(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    lead = models.ForeignKey('leads.Lead', on_delete=models.CASCADE, related_name='activities')
    
    ACTIVITY_TYPES = [
        ('lead_created', 'Lead Created'),
        ('lead_qualified', 'Lead Qualified'),
        ('email_sent', 'Email Sent'),
        ('status_changed', 'Status Changed'),
        ('followup_created', 'Follow-up Created'),
        ('followup_completed', 'Follow-up Completed'),
        ('note_added', 'Note Added'),
        ('assignment', 'Assignment'),
    ]
    activity_type = models.CharField(max_length=50, choices=ACTIVITY_TYPES)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.activity_type} on {self.lead}"

class LeadStatusHistory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    lead = models.ForeignKey('leads.Lead', on_delete=models.CASCADE, related_name='status_history')
    old_status = models.CharField(max_length=50)
    new_status = models.CharField(max_length=50)
    changed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-changed_at']

class LeadFollowUp(models.Model):
    class FollowUpType(models.TextChoices):
        CALL = 'call', 'Call'
        MEETING = 'meeting', 'Meeting'
        EMAIL = 'email', 'Email'
        DEMO = 'demo', 'Demo'
        OTHER = 'other', 'Other'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    lead = models.ForeignKey('leads.Lead', on_delete=models.CASCADE, related_name='followups')
    followup_type = models.CharField(max_length=20, choices=FollowUpType.choices, default=FollowUpType.OTHER)
    scheduled_at = models.DateTimeField()
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['scheduled_at']
        indexes = [
            models.Index(fields=['lead', 'status']),
            models.Index(fields=['scheduled_at']),
            models.Index(fields=['followup_type']),
        ]

    def __str__(self):
        return f"{self.get_followup_type_display()} for {self.lead} at {self.scheduled_at}"
