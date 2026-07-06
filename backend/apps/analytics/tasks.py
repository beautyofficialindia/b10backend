from .services.analytics_service import AnalyticsService


def log_analytics_event(event_type, conversation=None, lead=None, metadata=None):
    return AnalyticsService.track_event(event_type, conversation=conversation, lead=lead, metadata=metadata)
