class AnalyticsPeriods:
    TODAY = 'today'
    SEVEN_DAYS = '7d'
    THIRTY_DAYS = '30d'
    NINETY_DAYS = '90d'
    CUSTOM = 'custom'

    CHOICES = [
        (TODAY, 'Today'),
        (SEVEN_DAYS, 'Last 7 Days'),
        (THIRTY_DAYS, 'Last 30 Days'),
        (NINETY_DAYS, 'Last 90 Days'),
        (CUSTOM, 'Custom Range'),
    ]

    ALLOWED_PERIODS = [TODAY, SEVEN_DAYS, THIRTY_DAYS, NINETY_DAYS, CUSTOM]
    DEFAULT_PERIOD = THIRTY_DAYS
    CUSTOM_PERIOD_MAX_DAYS = 365

class HealthStatus:
    HEALTHY = 'healthy'
    WARNING = 'warning'
    DISABLED = 'disabled'
    ERROR = 'error'

class AnalyticsModules:
    CRM = 'crm'
    CHAT = 'chat'
    KNOWLEDGE = 'knowledge'
    ANALYTICS = 'analytics'
    USERS = 'users'
    LEADS = 'leads'

class ExportTypes:
    OVERVIEW = 'overview'
    LEADS = 'leads'
    CRM = 'crm'
    CHAT = 'chat'
    KNOWLEDGE = 'knowledge'
    USERS = 'users'
