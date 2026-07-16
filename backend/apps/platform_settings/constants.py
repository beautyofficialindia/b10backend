class SettingGroup:
    GENERAL = 'GENERAL'
    AI = 'AI'
    CRM = 'CRM'
    KNOWLEDGE_BASE = 'KNOWLEDGE_BASE'
    ANALYTICS = 'ANALYTICS'
    NOTIFICATIONS = 'NOTIFICATIONS'
    EMAIL = 'EMAIL'
    SECURITY = 'SECURITY'
    FEATURES = 'FEATURES'
    APPEARANCE = 'APPEARANCE'
    MAINTENANCE = 'MAINTENANCE'

    CHOICES = [
        (GENERAL, 'General'),
        (AI, 'AI'),
        (CRM, 'CRM'),
        (KNOWLEDGE_BASE, 'Knowledge Base'),
        (ANALYTICS, 'Analytics'),
        (NOTIFICATIONS, 'Notifications'),
        (EMAIL, 'Email'),
        (SECURITY, 'Security'),
        (FEATURES, 'Features'),
        (APPEARANCE, 'Appearance'),
        (MAINTENANCE, 'Maintenance'),
    ]

class ValueType:
    STRING = 'STRING'
    INTEGER = 'INTEGER'
    BOOLEAN = 'BOOLEAN'
    FLOAT = 'FLOAT'
    JSON = 'JSON'
    EMAIL = 'EMAIL'
    URL = 'URL'

    CHOICES = [
        (STRING, 'String'),
        (INTEGER, 'Integer'),
        (BOOLEAN, 'Boolean'),
        (FLOAT, 'Float'),
        (JSON, 'JSON'),
        (EMAIL, 'Email'),
        (URL, 'URL'),
    ]
