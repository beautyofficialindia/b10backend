from __future__ import annotations

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator, validate_email
from django.db import transaction
from django.db.models import Q, QuerySet

from apps.settings_management.models import Setting
from apps.user_management.models import UserAuditLog

User = get_user_model()


class SettingsService:
    """Encapsulates all business logic for settings management."""

    VALID_CATEGORIES = {
        'GENERAL', 'BRANDING', 'AI', 'CHATBOT',
        'NOTIFICATIONS', 'SECURITY', 'FEATURE_FLAGS', 'INTEGRATIONS',
    }

    NEVER_PUBLIC_CATEGORIES = {'INTEGRATIONS', 'SECURITY'}

    # Keys (or substrings) that indicate secret values within INTEGRATIONS
    SECRET_KEY_PATTERNS = {'api_key', 'secret_key', 'token', 'password', 'webhook_secret', 'private_key'}

    # Validation rules per category/key
    NUMERIC_SETTINGS = {
        ('AI', 'temperature'): (0.0, 2.0),
        ('AI', 'top_p'): (0.0, 1.0),
        ('AI', 'max_tokens'): (1, 100000),
        ('CHATBOT', 'typing_delay'): (0, 10000),
        ('CHATBOT', 'conversation_length'): (1, 1000),
        ('SECURITY', 'jwt_access_lifetime'): (1, 1440),
        ('SECURITY', 'jwt_refresh_lifetime'): (1, 43200),
        ('SECURITY', 'session_timeout'): (1, 525600),
    }

    BOOLEAN_SETTINGS = {
        ('AI', 'enable_streaming'),
        ('CHATBOT', 'lead_collection_enabled'),
        ('CHATBOT', 'memory_enabled'),
        ('NOTIFICATIONS', 'lead_notification_enabled'),
        ('NOTIFICATIONS', 'crm_notification_enabled'),
        ('FEATURE_FLAGS', 'analytics_enabled'),
        ('FEATURE_FLAGS', 'crm_enabled'),
        ('FEATURE_FLAGS', 'knowledge_base_enabled'),
        ('FEATURE_FLAGS', 'users_module_enabled'),
        ('FEATURE_FLAGS', 'roles_module_enabled'),
        ('FEATURE_FLAGS', 'notifications_enabled'),
        ('FEATURE_FLAGS', 'chatbot_enabled'),
    }

    URL_SETTINGS = {
        ('GENERAL', 'website'),
        ('BRANDING', 'logo_url'),
        ('BRANDING', 'favicon_url'),
    }

    EMAIL_SETTINGS = {
        ('GENERAL', 'company_email'),
        ('NOTIFICATIONS', 'admin_email'),
        ('NOTIFICATIONS', 'smtp_sender_email'),
    }

    # ─── Public methods ────────────────────────────────────────────────

    @staticmethod
    def list_settings(search: str | None = None, category: str | None = None) -> QuerySet:
        qs = Setting.objects.select_related('updated_by').all()
        if category:
            category_upper = category.upper()
            if category_upper not in SettingsService.VALID_CATEGORIES:
                raise ValidationError(
                    {'category': f"Invalid category. Valid: {', '.join(sorted(SettingsService.VALID_CATEGORIES))}"}
                )
            qs = qs.filter(category=category_upper)
        if search:
            qs = qs.filter(Q(key__icontains=search) | Q(description__icontains=search))
        return qs.order_by('category', 'key')

    @staticmethod
    def get_category_settings(category: str) -> QuerySet:
        category_upper = category.upper()
        if category_upper not in SettingsService.VALID_CATEGORIES:
            raise ValidationError(
                {'category': f"Invalid category. Valid: {', '.join(sorted(SettingsService.VALID_CATEGORIES))}"}
            )
        return Setting.objects.select_related('updated_by').filter(
            category=category_upper
        ).order_by('key')

    @staticmethod
    def get_setting(category: str, key: str) -> Setting:
        category_upper = category.upper()
        if category_upper not in SettingsService.VALID_CATEGORIES:
            raise ValidationError({'category': 'Invalid category.'})
        return Setting.objects.select_related('updated_by').get(
            category=category_upper, key=key
        )

    @staticmethod
    @transaction.atomic
    def update_category_settings(category: str, data: dict, actor: User) -> list[Setting]:
        category_upper = category.upper()
        if category_upper not in SettingsService.VALID_CATEGORIES:
            raise ValidationError(
                {'category': f"Invalid category. Valid: {', '.join(sorted(SettingsService.VALID_CATEGORIES))}"}
            )

        updated_settings = []
        changes = {}

        for key, value in data.items():
            # Validate
            SettingsService._validate_setting(category_upper, key, value)

            # Upsert
            setting, created = Setting.objects.get_or_create(
                category=category_upper,
                key=key,
                defaults={'value': value, 'updated_by': actor},
            )

            if not created:
                old_value = setting.value
                setting.value = value
                setting.updated_by = actor
                setting.save(update_fields=['value', 'updated_by', 'updated_at'])
                changes[key] = {'old': old_value, 'new': value}
            else:
                changes[key] = {'old': None, 'new': value}

            updated_settings.append(setting)

        # Audit log (mask secrets in metadata)
        safe_changes = SettingsService._mask_audit_changes(category_upper, changes)
        SettingsService._create_audit_log(
            actor=actor,
            action='settings_updated',
            description=f"Updated {len(data)} setting(s) in {category_upper}",
            metadata={
                'category': category_upper,
                'keys': list(data.keys()),
                'changes': safe_changes,
            },
        )

        return updated_settings

    @staticmethod
    def get_public_settings() -> QuerySet:
        return Setting.objects.filter(
            is_public=True,
        ).exclude(
            category__in=SettingsService.NEVER_PUBLIC_CATEGORIES,
        ).order_by('category', 'key')

    @staticmethod
    def mask_secret_value(setting: Setting):
        """Mask secret values for INTEGRATIONS category."""
        if setting.category != 'INTEGRATIONS':
            return setting.value

        if SettingsService._is_secret_key(setting.key):
            has_value = setting.value is not None and setting.value != '' and setting.value != {}
            return {'is_set': has_value}

        # For object values, mask nested secret keys
        if isinstance(setting.value, dict):
            masked = {}
            for k, v in setting.value.items():
                if SettingsService._is_secret_key(k):
                    masked[k] = {'is_set': v is not None and v != ''}
                else:
                    masked[k] = v
            return masked

        return setting.value

    # ─── Internal helpers ──────────────────────────────────────────────

    @staticmethod
    def _validate_setting(category: str, key: str, value) -> None:
        """Validate a setting value based on category and key rules."""
        # Numeric validation
        range_key = (category, key)
        if range_key in SettingsService.NUMERIC_SETTINGS:
            min_val, max_val = SettingsService.NUMERIC_SETTINGS[range_key]
            if value is not None and not isinstance(value, (int, float)):
                raise ValidationError(
                    {key: f"Must be a number between {min_val} and {max_val}."}
                )
            if value is not None and (value < min_val or value > max_val):
                raise ValidationError(
                    {key: f"Must be between {min_val} and {max_val}."}
                )

        # Boolean validation
        if range_key in SettingsService.BOOLEAN_SETTINGS:
            if value is not None and not isinstance(value, bool):
                raise ValidationError({key: "Must be a boolean (true/false)."})

        # URL validation
        if range_key in SettingsService.URL_SETTINGS:
            if value is not None and value != '':
                validator = URLValidator()
                try:
                    validator(value)
                except Exception:
                    raise ValidationError({key: "Must be a valid URL."})

        # Email validation
        if range_key in SettingsService.EMAIL_SETTINGS:
            if value is not None and value != '':
                try:
                    validate_email(value)
                except Exception:
                    raise ValidationError({key: "Must be a valid email address."})

    @staticmethod
    def _is_secret_key(key: str) -> bool:
        """Check if a key name indicates a secret value."""
        key_lower = key.lower()
        return any(pattern in key_lower for pattern in SettingsService.SECRET_KEY_PATTERNS)

    @staticmethod
    def _mask_audit_changes(category: str, changes: dict) -> dict:
        """Remove secret values from audit metadata."""
        if category != 'INTEGRATIONS':
            return changes

        masked = {}
        for key, change in changes.items():
            if SettingsService._is_secret_key(key):
                masked[key] = {'old': '***', 'new': '***'}
            elif isinstance(change.get('new'), dict):
                # Mask nested secrets in object values
                masked_change = {'old': {}, 'new': {}}
                for nested_key in change.get('new', {}):
                    if SettingsService._is_secret_key(nested_key):
                        masked_change['new'][nested_key] = '***'
                    else:
                        masked_change['new'][nested_key] = change['new'][nested_key]
                if isinstance(change.get('old'), dict):
                    for nested_key in change.get('old', {}):
                        if SettingsService._is_secret_key(nested_key):
                            masked_change['old'][nested_key] = '***'
                        else:
                            masked_change['old'][nested_key] = change['old'][nested_key]
                else:
                    masked_change['old'] = change.get('old')
                masked[key] = masked_change
            else:
                masked[key] = change
        return masked

    @staticmethod
    def _create_audit_log(
        actor: User,
        action: str,
        description: str,
        metadata: dict | None = None,
    ) -> None:
        UserAuditLog.objects.create(
            actor=actor,
            target_user=None,
            action=action,
            description=description,
            metadata=metadata or {},
        )
