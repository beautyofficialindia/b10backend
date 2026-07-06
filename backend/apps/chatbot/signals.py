from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.analytics.services.analytics_service import AnalyticsService
from .models import Feedback


@receiver(post_save, sender=Feedback)
def track_feedback_submission(sender, instance, created, **kwargs):
    if created:
        AnalyticsService.track_feedback_submitted(instance.session, instance.rating)
