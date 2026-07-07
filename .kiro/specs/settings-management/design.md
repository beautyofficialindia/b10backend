# Technical Design: Settings Management

## Overview

Generic key-value settings system using a single `Setting` model with JSONField values. Organized by categories, supports upsert, secret masking for integrations, public endpoint for frontend consumption, and audit logging. New app `apps/settings_management/`.

## Architecture

```
Client → JWT → core/urls.py → apps/settings_management/urls.py → SettingsViewSet
    → IsAdminUser (admin endpoints) / AllowAny (public endpoint)
    → SettingsService (business logic)
        → Setting ORM
        → UserAuditLog ORM
    → success_response / error_response
```

## Data Model

```python
class Setting(models.Model):
    CATEGORY_CHOICES = [
        ('GENERAL', 'General'),
        ('BRANDING', 'Branding'),
        ('AI', 'AI'),
        ('CHATBOT', 'Chatbot'),
        ('NOTIFICATIONS', 'Notifications'),
        ('SECURITY', 'Security'),
        ('FEATURE_FLAGS', 'Feature Flags'),
        ('INTEGRATIONS', 'Integrations'),
    ]

    id = models.BigAutoField(primary_key=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    key = models.CharField(max_length=100)
    value = models.JSONField(default=None, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    is_public = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='settings_updated',
    )

    class Meta:
        unique_together = [('category', 'key')]
        indexes = [
            models.Index(fields=['category']),
            models.Index(fields=['category', 'key']),
            models.Index(fields=['is_public']),
        ]
```

## URL Routing

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/api/v1/admin/settings/` | Admin | List all settings |
| GET | `/api/v1/admin/settings/{category}/` | Admin | Get category settings |
| PATCH | `/api/v1/admin/settings/{category}/` | Admin | Update category settings |
| GET | `/api/v1/settings/public/` | None | Public settings |

## Serializers

### SettingSerializer
- id, category, key, value, description, is_public, updated_at, updated_by_username

### SettingPublicSerializer
- category, key, value

### SettingUpdateSerializer
- settings: dict (key-value pairs to upsert)

## Service Layer — SettingsService

```python
class SettingsService:
    VALID_CATEGORIES = {'GENERAL', 'BRANDING', 'AI', 'CHATBOT', 'NOTIFICATIONS', 'SECURITY', 'FEATURE_FLAGS', 'INTEGRATIONS'}
    SECRET_CATEGORIES = {'INTEGRATIONS'}
    NEVER_PUBLIC_CATEGORIES = {'INTEGRATIONS', 'SECURITY'}

    # Keys within INTEGRATIONS that contain secrets
    SECRET_KEYS = {'api_key', 'secret_key', 'token', 'password', 'webhook_secret'}

    @staticmethod
    def list_settings(search=None, category=None) -> QuerySet

    @staticmethod
    def get_category_settings(category: str) -> QuerySet

    @staticmethod
    def update_category_settings(category: str, data: dict, actor: User) -> list[Setting]

    @staticmethod
    def get_public_settings() -> QuerySet

    @staticmethod
    def mask_secret_value(setting: Setting) -> any
        """Returns {'is_set': True/False} for secret fields instead of actual value."""

    @staticmethod
    def _create_audit_log(actor, category, changes, metadata=None) -> None
```

## Secret Masking Logic

For INTEGRATIONS category:
- If key contains any SECRET_KEYS substring (api_key, secret_key, token, password, webhook_secret): mask value as `{"is_set": true/false}`
- Other INTEGRATIONS keys (provider names, model names, URLs without secrets): show normally

## Default Settings Seed

Management command `seed_settings` creates defaults:

### GENERAL
- company_name, company_email, phone, website, address, social_links, timezone

### BRANDING
- logo_url, favicon_url, primary_color, secondary_color, footer_text, company_description

### AI
- provider, model, temperature, top_p, max_tokens, system_prompt, lead_qualification_prompt, extraction_prompt, enable_streaming

### CHATBOT
- welcome_message, suggested_questions, typing_delay, lead_collection_enabled, memory_enabled, conversation_length

### NOTIFICATIONS
- admin_email, lead_notification_enabled, crm_notification_enabled, smtp_sender_name, smtp_sender_email

### SECURITY
- jwt_access_lifetime, jwt_refresh_lifetime, password_policy, session_timeout, rate_limits

### FEATURE_FLAGS
- analytics_enabled, crm_enabled, knowledge_base_enabled, users_module_enabled, roles_module_enabled, notifications_enabled, chatbot_enabled

### INTEGRATIONS
- openrouter (object: {api_key, base_url}), openai (object: {api_key}), anthropic (object: {api_key}), gemini (object: {api_key}), resend (object: {api_key}), smtp (object: {host, port, username, password}), slack (object: {webhook_url}), webhook_url

## Error Handling

| Scenario | Status | Code |
|----------|--------|------|
| Invalid category | 400 | `invalid_category` |
| Validation error | 400 | `validation_error` |
| Not authenticated | 401 | — |
| Not admin | 403 | — |

## Audit Actions

| Action Value | Triggered By |
|-------------|-------------|
| `settings_updated` | PATCH /settings/{category}/ |
