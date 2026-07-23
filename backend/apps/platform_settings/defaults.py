from .constants import SettingGroup, ValueType
import json

# Recommended initial default platform settings
DEFAULT_PLATFORM_SETTINGS = [
    # GENERAL
    {
        'group': SettingGroup.GENERAL,
        'key': 'COMPANY_NAME',
        'display_name': 'Company Name',
        'value': 'B10 IT Solutions',
        'value_type': ValueType.STRING,
        'description': 'The official name of the company.',
        'is_public': True,
        'display_order': 1,
    },
    {
        'group': SettingGroup.GENERAL,
        'key': 'COMPANY_EMAIL',
        'display_name': 'Company Email',
        'value': 'contact@b10itsolutions.com',
        'value_type': ValueType.EMAIL,
        'description': 'The primary contact email for the company.',
        'is_public': True,
        'display_order': 2,
    },

    # FEATURES
    {
        'group': SettingGroup.FEATURES,
        'key': 'ENABLE_CRM',
        'display_name': 'Enable CRM',
        'value': 'true',
        'value_type': ValueType.BOOLEAN,
        'description': 'Toggle the CRM module globally.',
        'is_public': True,
        'display_order': 1,
    },
    {
        'group': SettingGroup.FEATURES,
        'key': 'ENABLE_KNOWLEDGE_BASE',
        'display_name': 'Enable Knowledge Base',
        'value': 'true',
        'value_type': ValueType.BOOLEAN,
        'description': 'Toggle the Knowledge Base module globally.',
        'is_public': True,
        'display_order': 2,
    },
    {
        'group': SettingGroup.FEATURES,
        'key': 'ENABLE_ANALYTICS',
        'display_name': 'Enable Analytics',
        'value': 'true',
        'value_type': ValueType.BOOLEAN,
        'description': 'Toggle the Analytics module globally.',
        'is_public': True,
        'display_order': 3,
    },
    {
        'group': SettingGroup.FEATURES,
        'key': 'ENABLE_AI_CHATBOT',
        'display_name': 'Enable AI Chatbot',
        'value': 'true',
        'value_type': ValueType.BOOLEAN,
        'description': 'Toggle the AI Chatbot functionality.',
        'is_public': True,
        'display_order': 4,
    },
    {
        'group': SettingGroup.FEATURES,
        'key': 'ENABLE_LEAD_QUALIFICATION',
        'display_name': 'Enable Lead Qualification',
        'value': 'true',
        'value_type': ValueType.BOOLEAN,
        'description': 'Toggle automatic AI lead qualification.',
        'is_public': False,
        'display_order': 5,
    },
    {
        'group': SettingGroup.FEATURES,
        'key': 'ENABLE_EMAIL_NOTIFICATIONS',
        'display_name': 'Enable Email Notifications',
        'value': 'true',
        'value_type': ValueType.BOOLEAN,
        'description': 'Toggle outgoing email notifications.',
        'is_public': False,
        'display_order': 6,
    },
    {
        'group': SettingGroup.FEATURES,
        'key': 'ENABLE_PUBLIC_CONTACT_FORM',
        'display_name': 'Enable Public Contact Form',
        'value': 'true',
        'value_type': ValueType.BOOLEAN,
        'description': 'Allow public users to submit contact inquiries.',
        'is_public': True,
        'display_order': 7,
    },

    # MAINTENANCE
    {
        'group': SettingGroup.MAINTENANCE,
        'key': 'MAINTENANCE_MODE',
        'display_name': 'Maintenance Mode',
        'value': 'false',
        'value_type': ValueType.BOOLEAN,
        'description': 'Put the entire platform into maintenance mode (blocks non-admin access).',
        'is_public': True,
        'display_order': 1,
    },
    {
        'group': SettingGroup.MAINTENANCE,
        'key': 'MAINTENANCE_BANNER_ENABLED',
        'display_name': 'Maintenance Banner Enabled',
        'value': 'false',
        'value_type': ValueType.BOOLEAN,
        'description': 'Display a maintenance warning banner across the platform.',
        'is_public': True,
        'display_order': 2,
    },
    {
        'group': SettingGroup.MAINTENANCE,
        'key': 'READ_ONLY_MODE',
        'display_name': 'Read Only Mode',
        'value': 'false',
        'value_type': ValueType.BOOLEAN,
        'description': 'Prevent all write operations across the platform.',
        'is_public': True,
        'display_order': 3,
    },
    {
        'group': SettingGroup.MAINTENANCE,
        'key': 'MAINTENANCE_MESSAGE',
        'display_name': 'Maintenance Message',
        'value': 'The platform is currently under maintenance. Please try again later.',
        'value_type': ValueType.STRING,
        'description': 'Message displayed when maintenance mode or banner is active.',
        'is_public': True,
        'display_order': 4,
    },

    # AI
    {
        'group': SettingGroup.AI,
        'key': 'DEFAULT_MODEL',
        'display_name': 'Default AI Model',
        'value': 'openai/gpt-4.1-mini',
        'value_type': ValueType.STRING,
        'description': 'The default LLM model to use across the platform.',
        'is_public': False,
        'display_order': 1,
    },
    {
        'group': SettingGroup.AI,
        'key': 'TEMPERATURE',
        'display_name': 'Temperature',
        'value': '0.7',
        'value_type': ValueType.FLOAT,
        'description': 'Controls randomness in AI responses (0.0 to 1.0).',
        'is_public': False,
        'display_order': 2,
        'validation_rules': {
            'min': 0,
            'max': 1
        }
    },
    {
        'group': SettingGroup.AI,
        'key': 'MAX_TOKENS',
        'display_name': 'Max Tokens',
        'value': '2048',
        'value_type': ValueType.INTEGER,
        'description': 'Maximum number of tokens to generate in AI responses.',
        'is_public': False,
        'display_order': 3,
        'validation_rules': {
            'min': 1
        }
    },
    {
        'group': SettingGroup.AI,
        'key': 'KNOWLEDGE_SOURCE',
        'display_name': 'Knowledge Source',
        'value': 'database',
        'value_type': ValueType.STRING,
        'description': 'The primary source of knowledge for the AI chatbot.',
        'is_public': False,
        'display_order': 4,
    },
    {
        'group': SettingGroup.AI,
        'key': 'CONTEXT_LIMITS',
        'display_name': 'Context Limits',
        'value': '10',
        'value_type': ValueType.INTEGER,
        'description': 'Maximum number of conversation turns or context entries to provide the AI.',
        'is_public': False,
        'display_order': 5,
        'validation_rules': {
            'min': 1,
            'max': 50
        }
    },

    # CRM
    {
        'group': SettingGroup.CRM,
        'key': 'AUTO_QUALIFICATION_ENABLED',
        'display_name': 'Auto Qualification Enabled',
        'value': 'true',
        'value_type': ValueType.BOOLEAN,
        'description': 'Automatically qualify leads using AI when created.',
        'is_public': False,
        'display_order': 1,
    },
    {
        'group': SettingGroup.CRM,
        'key': 'LEAD_SCORE_THRESHOLD',
        'display_name': 'Lead Score Threshold',
        'value': '70',
        'value_type': ValueType.INTEGER,
        'description': 'Minimum score required to automatically mark a lead as HOT.',
        'is_public': False,
        'display_order': 2,
        'validation_rules': {
            'min': 0,
            'max': 100
        }
    },
    {
        'group': SettingGroup.CRM,
        'key': 'DEFAULT_LEAD_PRIORITY',
        'display_name': 'Default Lead Priority',
        'value': 'medium',
        'value_type': ValueType.STRING,
        'description': 'Default priority assigned to newly created leads.',
        'is_public': False,
        'display_order': 3,
        'validation_rules': {
            'choices': ['low', 'medium', 'high']
        }
    },
    {
        'group': SettingGroup.CRM,
        'key': 'PIPELINE_SETTINGS',
        'display_name': 'Pipeline Settings',
        'value': json.dumps({
            "auto_assign": False,
            "enable_followups": True
        }),
        'value_type': ValueType.JSON,
        'description': 'Advanced CRM pipeline configuration rules.',
        'is_public': False,
        'display_order': 4,
    },

    # ANALYTICS

    {
        'group': SettingGroup.ANALYTICS,
        'key': 'TRACK_CONVERSATIONS',
        'display_name': 'Track Conversations',
        'value': 'true',
        'value_type': ValueType.BOOLEAN,
        'description': 'Log chatbot conversation metrics.',
        'is_public': False,
        'display_order': 2,
    },
    {
        'group': SettingGroup.ANALYTICS,
        'key': 'TRACK_LEADS',
        'display_name': 'Track Leads',
        'value': 'true',
        'value_type': ValueType.BOOLEAN,
        'description': 'Log lead generation and conversion metrics.',
        'is_public': False,
        'display_order': 3,
    },
    {
        'group': SettingGroup.ANALYTICS,
        'key': 'TRACK_CRM_ACTIONS',
        'display_name': 'Track CRM Actions',
        'value': 'true',
        'value_type': ValueType.BOOLEAN,
        'description': 'Log user actions within the CRM module.',
        'is_public': False,
        'display_order': 4,
    },
]
