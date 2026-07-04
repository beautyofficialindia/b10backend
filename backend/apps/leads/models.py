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
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Lead: {self.full_name or self.email or 'Anonymous'} ({self.status})"
