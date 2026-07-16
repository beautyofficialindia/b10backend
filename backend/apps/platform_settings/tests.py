from django.test import TestCase
from django.db.utils import IntegrityError
from django.core.cache import cache
from .models import PlatformSetting
from .constants import SettingGroup, ValueType
from .services import SettingsService
from .defaults import DEFAULT_PLATFORM_SETTINGS

class PlatformSettingModelTests(TestCase):
    def test_model_creation_success(self):
        setting = PlatformSetting.objects.create(
            group=SettingGroup.GENERAL,
            key='TEST_KEY',
            value='test_value',
            value_type=ValueType.STRING
        )
        self.assertIsNotNone(setting.id)
        self.assertEqual(setting.display_name, 'Test Key')

    def test_unique_constraint(self):
        PlatformSetting.objects.create(
            group=SettingGroup.AI,
            key='DEFAULT_MODEL',
            value='model_1',
            value_type=ValueType.STRING
        )
        with self.assertRaises(IntegrityError):
            PlatformSetting.objects.create(
                group=SettingGroup.AI,
                key='DEFAULT_MODEL',
                value='model_2',
                value_type=ValueType.STRING
            )

class SettingsServiceParsingTests(TestCase):
    def setUp(self):
        cache.clear()

    def test_parse_string(self):
        PlatformSetting.objects.create(
            group=SettingGroup.GENERAL,
            key='STR_KEY',
            value='hello',
            value_type=ValueType.STRING
        )
        val = SettingsService.get_setting(SettingGroup.GENERAL, 'STR_KEY')
        self.assertEqual(val, 'hello')

    def test_parse_integer(self):
        PlatformSetting.objects.create(
            group=SettingGroup.GENERAL,
            key='INT_KEY',
            value='42',
            value_type=ValueType.INTEGER
        )
        val = SettingsService.get_setting(SettingGroup.GENERAL, 'INT_KEY')
        self.assertEqual(val, 42)

    def test_parse_boolean_true(self):
        PlatformSetting.objects.create(
            group=SettingGroup.GENERAL,
            key='BOOL_TRUE',
            value='true',
            value_type=ValueType.BOOLEAN
        )
        val = SettingsService.get_setting(SettingGroup.GENERAL, 'BOOL_TRUE')
        self.assertTrue(val)

    def test_parse_boolean_false(self):
        PlatformSetting.objects.create(
            group=SettingGroup.GENERAL,
            key='BOOL_FALSE',
            value='0',
            value_type=ValueType.BOOLEAN
        )
        val = SettingsService.get_setting(SettingGroup.GENERAL, 'BOOL_FALSE')
        self.assertFalse(val)

    def test_invalid_type_parsing_boolean(self):
        PlatformSetting.objects.create(
            group=SettingGroup.GENERAL,
            key='BOOL_INVALID',
            value='hello',
            value_type=ValueType.BOOLEAN
        )
        with self.assertRaises(ValueError):
            SettingsService.get_setting(SettingGroup.GENERAL, 'BOOL_INVALID')

    def test_parse_float(self):
        PlatformSetting.objects.create(
            group=SettingGroup.GENERAL,
            key='FLOAT_KEY',
            value='3.14',
            value_type=ValueType.FLOAT
        )
        val = SettingsService.get_setting(SettingGroup.GENERAL, 'FLOAT_KEY')
        self.assertEqual(val, 3.14)

    def test_parse_json(self):
        PlatformSetting.objects.create(
            group=SettingGroup.GENERAL,
            key='JSON_KEY',
            value='{"theme": "dark"}',
            value_type=ValueType.JSON
        )
        val = SettingsService.get_setting(SettingGroup.GENERAL, 'JSON_KEY')
        self.assertEqual(val, {"theme": "dark"})

class SettingsServiceCachingTests(TestCase):
    def setUp(self):
        cache.clear()
        self.setting = PlatformSetting.objects.create(
            group=SettingGroup.CRM,
            key='TEST_CACHE',
            value='v1',
            value_type=ValueType.STRING
        )

    def test_get_setting_caches_value(self):
        val = SettingsService.get_setting(SettingGroup.CRM, 'TEST_CACHE')
        self.assertEqual(val, 'v1')
        
        # Modify DB directly to bypass signals
        PlatformSetting.objects.filter(id=self.setting.id).update(value='v2')
        
        # Should still get cached value
        val_cached = SettingsService.get_setting(SettingGroup.CRM, 'TEST_CACHE')
        self.assertEqual(val_cached, 'v1')

    def test_set_setting_invalidates_cache(self):
        SettingsService.get_setting(SettingGroup.CRM, 'TEST_CACHE')
        
        # Use service to update
        SettingsService.set_setting(SettingGroup.CRM, 'TEST_CACHE', 'v2')
        
        # Should get new value
        val = SettingsService.get_setting(SettingGroup.CRM, 'TEST_CACHE')
        self.assertEqual(val, 'v2')

    def test_signal_invalidates_cache_on_save(self):
        SettingsService.get_setting(SettingGroup.CRM, 'TEST_CACHE')
        
        self.setting.value = 'v2'
        self.setting.save() # Signal triggers
        
        val = SettingsService.get_setting(SettingGroup.CRM, 'TEST_CACHE')
        self.assertEqual(val, 'v2')

    def test_signal_invalidates_cache_on_delete(self):
        SettingsService.get_setting(SettingGroup.CRM, 'TEST_CACHE')
        self.setting.delete()
        
        val = SettingsService.get_setting(SettingGroup.CRM, 'TEST_CACHE')
        self.assertIsNone(val)

    def test_cache_refresh(self):
        SettingsService.get_setting(SettingGroup.CRM, 'TEST_CACHE')
        SettingsService.set_setting(SettingGroup.CRM, 'TEST_CACHE', 'new_val')
        
        # Invalidated and refreshed
        val = SettingsService.refresh_cache(SettingGroup.CRM, 'TEST_CACHE')
        self.assertEqual(val, 'new_val')

class SettingsServiceUtilityTests(TestCase):
    def setUp(self):
        cache.clear()

    def test_initialize_defaults(self):
        count = SettingsService.initialize_defaults()
        self.assertEqual(count, len(DEFAULT_PLATFORM_SETTINGS))
        
        # Second run should create 0
        count2 = SettingsService.initialize_defaults()
        self.assertEqual(count2, 0)

    def test_reset_defaults(self):
        SettingsService.initialize_defaults()
        
        # Change a default
        SettingsService.set_setting(SettingGroup.GENERAL, 'COMPANY_NAME', 'Changed')
        self.assertEqual(SettingsService.get_setting(SettingGroup.GENERAL, 'COMPANY_NAME'), 'Changed')
        
        # Reset
        SettingsService.reset_defaults()
        self.assertEqual(SettingsService.get_setting(SettingGroup.GENERAL, 'COMPANY_NAME'), 'B10 IT Solutions')

    def test_is_feature_enabled(self):
        PlatformSetting.objects.create(
            group=SettingGroup.FEATURES,
            key='NEW_FEATURE',
            value='true',
            value_type=ValueType.BOOLEAN
        )
        self.assertTrue(SettingsService.is_feature_enabled('NEW_FEATURE'))
        
        SettingsService.set_setting(SettingGroup.FEATURES, 'NEW_FEATURE', 'false')
        self.assertFalse(SettingsService.is_feature_enabled('NEW_FEATURE'))

    def test_get_group(self):
        PlatformSetting.objects.create(group=SettingGroup.AI, key='K1', value='1', value_type=ValueType.INTEGER)
        PlatformSetting.objects.create(group=SettingGroup.AI, key='K2', value='2', value_type=ValueType.INTEGER)
        
        group_settings = SettingsService.get_group(SettingGroup.AI)
        self.assertEqual(group_settings, {'K1': 1, 'K2': 2})

    def test_get_all_settings(self):
        PlatformSetting.objects.create(group=SettingGroup.AI, key='K1', value='1', value_type=ValueType.INTEGER)
        PlatformSetting.objects.create(group=SettingGroup.CRM, key='C1', value='true', value_type=ValueType.BOOLEAN)
        
        all_settings = SettingsService.get_all_settings()
        self.assertEqual(all_settings[SettingGroup.AI]['K1'], 1)
        self.assertEqual(all_settings[SettingGroup.CRM]['C1'], True)

    def test_convenience_getters(self):
        PlatformSetting.objects.create(group=SettingGroup.GENERAL, key='B', value='true', value_type=ValueType.BOOLEAN)
        PlatformSetting.objects.create(group=SettingGroup.GENERAL, key='I', value='99', value_type=ValueType.INTEGER)
        PlatformSetting.objects.create(group=SettingGroup.GENERAL, key='J', value='{"a":1}', value_type=ValueType.JSON)
        PlatformSetting.objects.create(group=SettingGroup.GENERAL, key='E', value='test@test.com', value_type=ValueType.EMAIL)
        PlatformSetting.objects.create(group=SettingGroup.GENERAL, key='U', value='https://b10.com', value_type=ValueType.URL)
        
        self.assertTrue(SettingsService.get_boolean(SettingGroup.GENERAL, 'B'))
        self.assertEqual(SettingsService.get_integer(SettingGroup.GENERAL, 'I'), 99)
        self.assertEqual(SettingsService.get_json(SettingGroup.GENERAL, 'J'), {"a": 1})
        self.assertEqual(SettingsService.get_email(SettingGroup.GENERAL, 'E'), 'test@test.com')
        self.assertEqual(SettingsService.get_url(SettingGroup.GENERAL, 'U'), 'https://b10.com')
