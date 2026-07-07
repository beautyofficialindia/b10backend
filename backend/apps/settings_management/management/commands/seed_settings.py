"""Management command to seed default settings."""
from django.core.management.base import BaseCommand

from apps.settings_management.models import Setting

DEFAULT_SETTINGS = [
    # ─── GENERAL ───────────────────────────────────────────────────────
    {'category': 'GENERAL', 'key': 'company_name', 'value': 'B10 IT Solution', 'description': 'Company display name', 'is_public': True},
    {'category': 'GENERAL', 'key': 'company_email', 'value': 'info@b10itsolution.com', 'description': 'Company contact email', 'is_public': True},
    {'category': 'GENERAL', 'key': 'phone', 'value': '', 'description': 'Company phone number', 'is_public': True},
    {'category': 'GENERAL', 'key': 'website', 'value': 'https://b10itsolution.com', 'description': 'Company website URL', 'is_public': True},
    {'category': 'GENERAL', 'key': 'address', 'value': '', 'description': 'Company physical address', 'is_public': True},
    {'category': 'GENERAL', 'key': 'social_links', 'value': {'linkedin': '', 'twitter': '', 'facebook': '', 'instagram': ''}, 'description': 'Social media links', 'is_public': True},
    {'category': 'GENERAL', 'key': 'timezone', 'value': 'UTC', 'description': 'Default timezone', 'is_public': True},

    # ─── BRANDING ──────────────────────────────────────────────────────
    {'category': 'BRANDING', 'key': 'logo_url', 'value': '', 'description': 'Company logo URL', 'is_public': True},
    {'category': 'BRANDING', 'key': 'favicon_url', 'value': '', 'description': 'Favicon URL', 'is_public': True},
    {'category': 'BRANDING', 'key': 'primary_color', 'value': '#1a73e8', 'description': 'Primary brand color', 'is_public': True},
    {'category': 'BRANDING', 'key': 'secondary_color', 'value': '#4285f4', 'description': 'Secondary brand color', 'is_public': True},
    {'category': 'BRANDING', 'key': 'footer_text', 'value': '© 2024 B10 IT Solution. All rights reserved.', 'description': 'Footer text', 'is_public': True},
    {'category': 'BRANDING', 'key': 'company_description', 'value': '', 'description': 'Short company description', 'is_public': True},

    # ─── AI ────────────────────────────────────────────────────────────
    {'category': 'AI', 'key': 'provider', 'value': 'openrouter', 'description': 'AI provider (openrouter, openai, anthropic, gemini)', 'is_public': False},
    {'category': 'AI', 'key': 'model', 'value': 'openai/gpt-4o-mini', 'description': 'AI model identifier', 'is_public': False},
    {'category': 'AI', 'key': 'temperature', 'value': 0.7, 'description': 'Model temperature (0.0-2.0)', 'is_public': False},
    {'category': 'AI', 'key': 'top_p', 'value': 1.0, 'description': 'Top P sampling (0.0-1.0)', 'is_public': False},
    {'category': 'AI', 'key': 'max_tokens', 'value': 1024, 'description': 'Maximum response tokens', 'is_public': False},
    {'category': 'AI', 'key': 'system_prompt', 'value': '', 'description': 'System prompt for AI conversations', 'is_public': False},
    {'category': 'AI', 'key': 'lead_qualification_prompt', 'value': '', 'description': 'Prompt for lead qualification', 'is_public': False},
    {'category': 'AI', 'key': 'extraction_prompt', 'value': '', 'description': 'Prompt for data extraction', 'is_public': False},
    {'category': 'AI', 'key': 'enable_streaming', 'value': False, 'description': 'Enable streaming responses', 'is_public': False},

    # ─── CHATBOT ───────────────────────────────────────────────────────
    {'category': 'CHATBOT', 'key': 'welcome_message', 'value': 'Hello! How can I help you today?', 'description': 'Chatbot welcome message', 'is_public': True},
    {'category': 'CHATBOT', 'key': 'suggested_questions', 'value': ['What services do you offer?', 'How can I contact you?', 'Tell me about your pricing'], 'description': 'Suggested questions for users', 'is_public': True},
    {'category': 'CHATBOT', 'key': 'typing_delay', 'value': 500, 'description': 'Typing indicator delay in ms', 'is_public': True},
    {'category': 'CHATBOT', 'key': 'lead_collection_enabled', 'value': True, 'description': 'Enable lead collection during chat', 'is_public': False},
    {'category': 'CHATBOT', 'key': 'memory_enabled', 'value': True, 'description': 'Enable conversation memory', 'is_public': False},
    {'category': 'CHATBOT', 'key': 'conversation_length', 'value': 50, 'description': 'Max messages per conversation', 'is_public': False},

    # ─── NOTIFICATIONS ─────────────────────────────────────────────────
    {'category': 'NOTIFICATIONS', 'key': 'admin_email', 'value': '', 'description': 'Admin notification email', 'is_public': False},
    {'category': 'NOTIFICATIONS', 'key': 'lead_notification_enabled', 'value': True, 'description': 'Enable lead notifications', 'is_public': False},
    {'category': 'NOTIFICATIONS', 'key': 'crm_notification_enabled', 'value': False, 'description': 'Enable CRM notifications', 'is_public': False},
    {'category': 'NOTIFICATIONS', 'key': 'smtp_sender_name', 'value': 'B10 IT Solution', 'description': 'SMTP sender display name', 'is_public': False},
    {'category': 'NOTIFICATIONS', 'key': 'smtp_sender_email', 'value': 'noreply@b10itsolution.com', 'description': 'SMTP sender email', 'is_public': False},

    # ─── SECURITY ──────────────────────────────────────────────────────
    {'category': 'SECURITY', 'key': 'jwt_access_lifetime', 'value': 15, 'description': 'JWT access token lifetime in minutes', 'is_public': False},
    {'category': 'SECURITY', 'key': 'jwt_refresh_lifetime', 'value': 10080, 'description': 'JWT refresh token lifetime in minutes', 'is_public': False},
    {'category': 'SECURITY', 'key': 'password_policy', 'value': {'min_length': 8, 'require_uppercase': True, 'require_number': True, 'require_special': False}, 'description': 'Password policy configuration', 'is_public': False},
    {'category': 'SECURITY', 'key': 'session_timeout', 'value': 30, 'description': 'Session timeout in minutes', 'is_public': False},
    {'category': 'SECURITY', 'key': 'rate_limits', 'value': {'anon': '10/min', 'user': '100/min'}, 'description': 'API rate limits', 'is_public': False},

    # ─── FEATURE_FLAGS ─────────────────────────────────────────────────
    {'category': 'FEATURE_FLAGS', 'key': 'analytics_enabled', 'value': True, 'description': 'Enable analytics module', 'is_public': True},
    {'category': 'FEATURE_FLAGS', 'key': 'crm_enabled', 'value': True, 'description': 'Enable CRM module', 'is_public': True},
    {'category': 'FEATURE_FLAGS', 'key': 'knowledge_base_enabled', 'value': True, 'description': 'Enable knowledge base module', 'is_public': True},
    {'category': 'FEATURE_FLAGS', 'key': 'users_module_enabled', 'value': True, 'description': 'Enable users management module', 'is_public': True},
    {'category': 'FEATURE_FLAGS', 'key': 'roles_module_enabled', 'value': True, 'description': 'Enable roles management module', 'is_public': True},
    {'category': 'FEATURE_FLAGS', 'key': 'notifications_enabled', 'value': True, 'description': 'Enable notifications module', 'is_public': True},
    {'category': 'FEATURE_FLAGS', 'key': 'chatbot_enabled', 'value': True, 'description': 'Enable chatbot module', 'is_public': True},

    # ─── INTEGRATIONS ──────────────────────────────────────────────────
    {'category': 'INTEGRATIONS', 'key': 'openrouter', 'value': {'api_key': '', 'base_url': 'https://openrouter.ai/api/v1'}, 'description': 'OpenRouter configuration', 'is_public': False},
    {'category': 'INTEGRATIONS', 'key': 'openai', 'value': {'api_key': ''}, 'description': 'OpenAI configuration', 'is_public': False},
    {'category': 'INTEGRATIONS', 'key': 'anthropic', 'value': {'api_key': ''}, 'description': 'Anthropic configuration', 'is_public': False},
    {'category': 'INTEGRATIONS', 'key': 'gemini', 'value': {'api_key': ''}, 'description': 'Google Gemini configuration', 'is_public': False},
    {'category': 'INTEGRATIONS', 'key': 'resend', 'value': {'api_key': ''}, 'description': 'Resend email configuration', 'is_public': False},
    {'category': 'INTEGRATIONS', 'key': 'smtp', 'value': {'host': '', 'port': 587, 'username': '', 'password': ''}, 'description': 'SMTP configuration', 'is_public': False},
    {'category': 'INTEGRATIONS', 'key': 'slack', 'value': {'webhook_url': ''}, 'description': 'Slack integration', 'is_public': False},
    {'category': 'INTEGRATIONS', 'key': 'webhook_url', 'value': '', 'description': 'General webhook URL', 'is_public': False},
]


class Command(BaseCommand):
    help = 'Seed default settings for all categories'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Overwrite existing settings with defaults',
        )

    def handle(self, *args, **options):
        force = options['force']
        created = 0
        updated = 0
        skipped = 0

        for item in DEFAULT_SETTINGS:
            setting, was_created = Setting.objects.get_or_create(
                category=item['category'],
                key=item['key'],
                defaults={
                    'value': item['value'],
                    'description': item['description'],
                    'is_public': item['is_public'],
                },
            )

            if was_created:
                created += 1
            elif force:
                setting.value = item['value']
                setting.description = item['description']
                setting.is_public = item['is_public']
                setting.save(update_fields=['value', 'description', 'is_public', 'updated_at'])
                updated += 1
            else:
                skipped += 1

        self.stdout.write('')
        self.stdout.write(f'Created: {created}')
        self.stdout.write(f'Updated: {updated}')
        self.stdout.write(f'Skipped: {skipped}')
        self.stdout.write(f'Total:   {len(DEFAULT_SETTINGS)}')
        self.stdout.write(self.style.SUCCESS('Done.'))
