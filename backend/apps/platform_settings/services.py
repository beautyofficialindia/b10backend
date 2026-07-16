import json
from django.core.cache import cache
from .models import PlatformSetting
from .constants import ValueType
from .defaults import DEFAULT_PLATFORM_SETTINGS

class SettingsService:
    """Service layer for managing platform settings with caching and type parsing."""

    CACHE_KEY_ALL = 'settings:all'
    CACHE_KEY_GROUP_PREFIX = 'settings:group:'
    CACHE_KEY_KEY_PREFIX = 'settings:key:'

    @classmethod
    def _get_cache_key(cls, group, key):
        return f"{cls.CACHE_KEY_KEY_PREFIX}{group}:{key}"

    @classmethod
    def _get_group_cache_key(cls, group):
        return f"{cls.CACHE_KEY_GROUP_PREFIX}{group}"

    @classmethod
    def get_setting(cls, group, key):
        """Retrieve a setting and parse its value based on value_type."""
        cache_key = cls._get_cache_key(group, key)
        cached_value = cache.get(cache_key)
        
        if cached_value is not None:
            return cached_value

        try:
            setting = PlatformSetting.objects.get(group=group, key=key)
            parsed_value = cls._parse_value(setting.value, setting.value_type)
            cache.set(cache_key, parsed_value, timeout=None)
            return parsed_value
        except PlatformSetting.DoesNotExist:
            return None

    @classmethod
    def _parse_value(cls, value, value_type):
        """Parse raw text value into proper Python types."""
        if not value:
            return None
            
        if value_type == ValueType.STRING:
            return value
        elif value_type == ValueType.INTEGER:
            return int(value)
        elif value_type == ValueType.BOOLEAN:
            val_lower = value.lower()
            if val_lower in ('true', '1', 'yes', 't'):
                return True
            elif val_lower in ('false', '0', 'no', 'f'):
                return False
            raise ValueError(f"Invalid boolean value: {value}")
        elif value_type == ValueType.FLOAT:
            return float(value)
        elif value_type == ValueType.JSON:
            return json.loads(value)
        elif value_type in (ValueType.EMAIL, ValueType.URL):
            return value
        return value

    @classmethod
    def set_setting(cls, group, key, value, user=None):
        """Update or create a setting and invalidate its cache."""
        setting = PlatformSetting.objects.filter(group=group, key=key).first()
        if not setting:
            raise ValueError(f"Setting {group}:{key} does not exist. Use create_setting.")
        
        setting.value = str(value)
        if user:
            setting.updated_by = user
        setting.save() # Signals will handle cache invalidation
        return setting

    @classmethod
    def get_group(cls, group):
        """Retrieve all settings for a specific group."""
        cache_key = cls._get_group_cache_key(group)
        cached_group = cache.get(cache_key)
        
        if cached_group is not None:
            return cached_group
            
        settings = PlatformSetting.objects.filter(group=group)
        result = {s.key: cls._parse_value(s.value, s.value_type) for s in settings}
        cache.set(cache_key, result, timeout=None)
        return result

    @classmethod
    def create_setting(cls, **kwargs):
        """Create a new setting. Enforces uniqueness."""
        setting = PlatformSetting.objects.create(**kwargs)
        return setting

    @classmethod
    def delete_setting(cls, group, key):
        """Delete a setting."""
        setting = PlatformSetting.objects.filter(group=group, key=key).first()
        if setting:
            setting.delete() # Signals will handle cache invalidation
            return True
        return False

    @classmethod
    def initialize_defaults(cls, user=None):
        """Seed the database with default settings from defaults.py without overwriting existing ones."""
        created_count = 0
        for default in DEFAULT_PLATFORM_SETTINGS:
            obj, created = PlatformSetting.objects.get_or_create(
                group=default['group'],
                key=default['key'],
                defaults={
                    'display_name': default.get('display_name', ''),
                    'value': default.get('value', ''),
                    'value_type': default.get('value_type', ValueType.STRING),
                    'description': default.get('description', ''),
                    'is_public': default.get('is_public', False),
                    'display_order': default.get('display_order', 0),
                    'validation_rules': default.get('validation_rules', {}),
                    'updated_by': user
                }
            )
            if created:
                created_count += 1
        
        # Clear global caches just in case
        cls.clear_cache(None, None)
        return created_count

    @classmethod
    def reset_defaults(cls, user=None):
        """Force reset all default settings to their original values."""
        reset_count = 0
        for default in DEFAULT_PLATFORM_SETTINGS:
            setting = PlatformSetting.objects.filter(group=default['group'], key=default['key']).first()
            if setting:
                setting.value = default.get('value', '')
                if user:
                    setting.updated_by = user
                setting.save()
                reset_count += 1
            else:
                cls.create_setting(**default, updated_by=user)
                reset_count += 1
        return reset_count

    @classmethod
    def is_feature_enabled(cls, key):
        """Convenience method for checking feature flags in the FEATURES group."""
        val = cls.get_setting('FEATURES', key)
        return bool(val)

    @classmethod
    def get_boolean(cls, group, key):
        return bool(cls.get_setting(group, key))

    @classmethod
    def get_integer(cls, group, key):
        val = cls.get_setting(group, key)
        return int(val) if val is not None else None

    @classmethod
    def get_json(cls, group, key):
        val = cls.get_setting(group, key)
        return val if isinstance(val, dict) or isinstance(val, list) else None

    @classmethod
    def get_email(cls, group, key):
        return cls.get_setting(group, key)

    @classmethod
    def get_url(cls, group, key):
        return cls.get_setting(group, key)

    @classmethod
    def clear_cache(cls, group=None, key=None):
        """Clear cache for a specific key, a group, or all settings."""
        if group and key:
            cache.delete(cls._get_cache_key(group, key))
            cache.delete(cls._get_group_cache_key(group))
            cache.delete(cls.CACHE_KEY_ALL)
        elif group:
            cache.delete(cls._get_group_cache_key(group))
            # Must also clear individual keys or all? Easiest to clear all for group updates
            cache.delete(cls.CACHE_KEY_ALL)
        else:
            cache.delete(cls.CACHE_KEY_ALL)

    @classmethod
    def refresh_cache(cls, group, key):
        """Force refresh the cache for a specific setting."""
        cls.clear_cache(group, key)
        return cls.get_setting(group, key)

    @classmethod
    def get_all_settings(cls):
        """Retrieve all settings as a nested dictionary."""
        cached_all = cache.get(cls.CACHE_KEY_ALL)
        if cached_all is not None:
            return cached_all
            
        settings = PlatformSetting.objects.all()
        result = {}
        for s in settings:
            if s.group not in result:
                result[s.group] = {}
            result[s.group][s.key] = cls._parse_value(s.value, s.value_type)
            
        cache.set(cls.CACHE_KEY_ALL, result, timeout=None)
        return result
