from django.db import models
from django.utils import timezone
import uuid

class ConversationSession(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('idle', 'Idle'),
        ('closed', 'Closed'),
        ('escalated', 'Escalated'),
        ('abandoned', 'Abandoned'),
    ]
    QUALIFICATION_STATE_CHOICES = [
        ('not_started', 'Not Started'),
        ('gathering', 'Gathering'),
        ('qualified', 'Qualified'),
        ('disqualified', 'Disqualified'),
        ('escalated_to_human', 'Escalated To Human'),
    ]
    CHANNEL_CHOICES = [
        ('web_widget', 'Web Widget'),
        ('api', 'API'),
        ('whatsapp', 'WhatsApp'),
        ('other', 'Other'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session_id = models.UUIDField(unique=True, default=uuid.uuid4)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    qualification_state = models.CharField(max_length=30, choices=QUALIFICATION_STATE_CHOICES, default='not_started')
    channel = models.CharField(max_length=20, choices=CHANNEL_CHOICES, default='web_widget')
    locale = models.CharField(max_length=20, null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_message_at = models.DateTimeField(auto_now_add=True)
    escalated_at = models.DateTimeField(null=True, blank=True)
    closed_at = models.DateTimeField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return str(self.session_id)

class Message(models.Model):
    ROLE_CHOICES = [
        ('user', 'User'),
        ('assistant', 'Assistant'),
        ('system', 'System'),
    ]
    MESSAGE_TYPE_CHOICES = [
        ('text', 'Text'),
        ('quick_reply', 'Quick Reply'),
        ('card', 'Card'),
        ('form', 'Form'),
        ('system_event', 'System Event'),
    ]
    session = models.ForeignKey(ConversationSession, on_delete=models.CASCADE, related_name='messages')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    content = models.TextField()
    sequence_number = models.PositiveIntegerField(null=True, blank=True)
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPE_CHOICES, default='text')
    response_metadata = models.JSONField(default=dict, blank=True)
    token_count_input = models.PositiveIntegerField(null=True, blank=True)
    token_count_output = models.PositiveIntegerField(null=True, blank=True)
    processing_time_ms = models.PositiveIntegerField(null=True, blank=True)
    error_code = models.CharField(max_length=100, null=True, blank=True)
    error_detail = models.TextField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['session', 'sequence_number'],
                name='uq_message_session_sequence',
                condition=models.Q(sequence_number__isnull=False),
            )
        ]

    def __str__(self):
        return f"{self.role}: {self.content[:50]}"


class Feedback(models.Model):
    RATING_CHOICES = [
        ('positive', 'Positive'),
        ('negative', 'Negative'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(ConversationSession, on_delete=models.CASCADE, related_name='feedback')
    message = models.ForeignKey(Message, on_delete=models.CASCADE, null=True, blank=True, related_name='feedback')
    rating = models.CharField(max_length=20, choices=RATING_CHOICES)
    comment = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
