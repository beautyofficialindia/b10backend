"""Comprehensive tests for Settings Management module."""
from django.core.management import call_command
from django.contrib.auth import get_user_model
from io import StringIO

from apps.settings_management.models import Setting
from apps.settings_management.tests.conftest import BaseSettingsTest
from apps.user_management.models import UserAuditLog

User = get_user_model()


# ═══════════════════════════════════════════════════════════════════
# 1. Authentication & Authorization
# ═══════════════════════════════════════════════════════════════════

class AuthTests(BaseSettingsTest):
    def test_anon_list_401(self):
        self.assertEqual(self.anon_client.get('/api/v1/admin/settings/').status_code, 401)

    def test_anon_category_401(self):
        self.assertEqual(self.anon_client.get('/api/v1/admin/settings/GENERAL/').status_code, 401)

    def test_anon_update_401(self):
        self.assertEqual(self.anon_client.patch('/api/v1/admin/settings/GENERAL/', {}, format='json').status_code, 401)

    def test_nonadmin_list_403(self):
        self.assertEqual(self.regular_client.get('/api/v1/admin/settings/').status_code, 403)

    def test_nonadmin_update_403(self):
        self.assertEqual(self.regular_client.patch('/api/v1/admin/settings/GENERAL/', {}, format='json').status_code, 403)

    def test_admin_list_200(self):
        self.assertEqual(self.admin_client.get('/api/v1/admin/settings/').status_code, 200)

    def test_public_endpoint_no_auth(self):
        resp = self.anon_client.get('/api/v1/admin/settings/public/')
        self.assertEqual(resp.status_code, 200)


# ═══════════════════════════════════════════════════════════════════
# 2. Public Endpoint
# ═══════════════════════════════════════════════════════════════════

class PublicEndpointTests(BaseSettingsTest):
    def test_returns_only_public_settings(self):
        resp = self.anon_client.get('/api/v1/admin/settings/public/')
        data = resp.json()['data']
        for s in data:
            self.assertNotEqual(s['category'], 'INTEGRATIONS')
            self.assertNotEqual(s['category'], 'SECURITY')

    def test_public_includes_public_flag_settings(self):
        resp = self.anon_client.get('/api/v1/admin/settings/public/')
        keys = [s['key'] for s in resp.json()['data']]
        self.assertIn('company_name', keys)
        self.assertIn('primary_color', keys)

    def test_public_excludes_private_settings(self):
        resp = self.anon_client.get('/api/v1/admin/settings/public/')
        keys = [s['key'] for s in resp.json()['data']]
        self.assertNotIn('temperature', keys)

    def test_public_serializer_fields(self):
        resp = self.anon_client.get('/api/v1/admin/settings/public/')
        for s in resp.json()['data']:
            self.assertEqual(set(s.keys()), {'category', 'key', 'value'})


# ═══════════════════════════════════════════════════════════════════
# 3. Admin List Endpoint
# ═══════════════════════════════════════════════════════════════════

class ListSettingsTests(BaseSettingsTest):
    def test_list_all(self):
        resp = self.admin_client.get('/api/v1/admin/settings/')
        self.assertEqual(resp.status_code, 200)
        self.assertGreater(len(resp.json()['data']), 0)

    def test_list_filter_by_category(self):
        resp = self.admin_client.get('/api/v1/admin/settings/?category=AI')
        data = resp.json()['data']
        for s in data:
            self.assertEqual(s['category'], 'AI')

    def test_list_search(self):
        resp = self.admin_client.get('/api/v1/admin/settings/?search=company')
        data = resp.json()['data']
        self.assertGreater(len(data), 0)

    def test_list_invalid_category_400(self):
        resp = self.admin_client.get('/api/v1/admin/settings/?category=INVALID')
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.json()['code'], 'invalid_category')

    def test_list_masks_integration_secrets(self):
        resp = self.admin_client.get('/api/v1/admin/settings/')
        data = resp.json()['data']
        integration_settings = [s for s in data if s['category'] == 'INTEGRATIONS']
        for s in integration_settings:
            if isinstance(s['value'], dict):
                for k, v in s['value'].items():
                    if 'api_key' in k or 'password' in k:
                        self.assertEqual(v, {'is_set': True})


# ═══════════════════════════════════════════════════════════════════
# 4. Category Retrieval
# ═══════════════════════════════════════════════════════════════════

class CategoryTests(BaseSettingsTest):
    def test_get_category(self):
        resp = self.admin_client.get('/api/v1/admin/settings/GENERAL/')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()['data']
        for s in data:
            self.assertEqual(s['category'], 'GENERAL')

    def test_get_category_case_insensitive(self):
        resp = self.admin_client.get('/api/v1/admin/settings/general/')
        self.assertEqual(resp.status_code, 200)

    def test_get_invalid_category_400(self):
        resp = self.admin_client.get('/api/v1/admin/settings/FAKE/')
        self.assertEqual(resp.status_code, 400)

    def test_category_masks_secrets(self):
        resp = self.admin_client.get('/api/v1/admin/settings/INTEGRATIONS/')
        data = resp.json()['data']
        openrouter = next((s for s in data if s['key'] == 'openrouter'), None)
        self.assertIsNotNone(openrouter)
        self.assertEqual(openrouter['value']['api_key'], {'is_set': True})
        # base_url should NOT be masked
        self.assertEqual(openrouter['value']['base_url'], 'https://api.openrouter.ai')


# ═══════════════════════════════════════════════════════════════════
# 5. Update Settings
# ═══════════════════════════════════════════════════════════════════

class UpdateSettingsTests(BaseSettingsTest):
    def test_update_existing_setting(self):
        resp = self.admin_client.patch('/api/v1/admin/settings/GENERAL/', {
            'settings': {'company_name': 'NewCo'}
        }, format='json')
        self.assertEqual(resp.status_code, 200)
        setting = Setting.objects.get(category='GENERAL', key='company_name')
        self.assertEqual(setting.value, 'NewCo')
        self.assertEqual(setting.updated_by, self.admin_user)

    def test_update_creates_new_setting(self):
        resp = self.admin_client.patch('/api/v1/admin/settings/GENERAL/', {
            'settings': {'new_key': 'new_value'}
        }, format='json')
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(Setting.objects.filter(category='GENERAL', key='new_key').exists())

    def test_update_invalid_category_400(self):
        resp = self.admin_client.patch('/api/v1/admin/settings/FAKE/', {
            'settings': {'key': 'val'}
        }, format='json')
        self.assertEqual(resp.status_code, 400)

    def test_update_validates_numeric_range(self):
        resp = self.admin_client.patch('/api/v1/admin/settings/AI/', {
            'settings': {'temperature': 5.0}
        }, format='json')
        self.assertEqual(resp.status_code, 400)

    def test_update_validates_boolean(self):
        resp = self.admin_client.patch('/api/v1/admin/settings/FEATURE_FLAGS/', {
            'settings': {'analytics_enabled': 'not_a_bool'}
        }, format='json')
        self.assertEqual(resp.status_code, 400)

    def test_update_validates_url(self):
        resp = self.admin_client.patch('/api/v1/admin/settings/BRANDING/', {
            'settings': {'logo_url': 'not-a-url'}
        }, format='json')
        self.assertEqual(resp.status_code, 400)

    def test_update_validates_email(self):
        resp = self.admin_client.patch('/api/v1/admin/settings/NOTIFICATIONS/', {
            'settings': {'admin_email': 'not-an-email'}
        }, format='json')
        self.assertEqual(resp.status_code, 400)

    def test_update_multiple_settings(self):
        resp = self.admin_client.patch('/api/v1/admin/settings/AI/', {
            'settings': {'temperature': 0.5, 'model': 'claude-3'}
        }, format='json')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(Setting.objects.get(category='AI', key='temperature').value, 0.5)
        self.assertEqual(Setting.objects.get(category='AI', key='model').value, 'claude-3')

    def test_update_json_object_value(self):
        resp = self.admin_client.patch('/api/v1/admin/settings/INTEGRATIONS/', {
            'settings': {'openrouter': {'api_key': 'new-key', 'base_url': 'https://new.url'}}
        }, format='json')
        self.assertEqual(resp.status_code, 200)
        setting = Setting.objects.get(category='INTEGRATIONS', key='openrouter')
        self.assertEqual(setting.value['api_key'], 'new-key')

    def test_update_null_value(self):
        resp = self.admin_client.patch('/api/v1/admin/settings/GENERAL/', {
            'settings': {'phone': None}
        }, format='json')
        self.assertEqual(resp.status_code, 200)

    def test_update_missing_settings_key_400(self):
        resp = self.admin_client.patch('/api/v1/admin/settings/GENERAL/', {}, format='json')
        self.assertEqual(resp.status_code, 400)


# ═══════════════════════════════════════════════════════════════════
# 6. Audit Logging
# ═══════════════════════════════════════════════════════════════════

class AuditLogTests(BaseSettingsTest):
    def test_update_creates_audit_log(self):
        self.admin_client.patch('/api/v1/admin/settings/GENERAL/', {
            'settings': {'company_name': 'Audited'}
        }, format='json')
        log = UserAuditLog.objects.filter(action='settings_updated').first()
        self.assertIsNotNone(log)
        self.assertEqual(log.actor, self.admin_user)
        self.assertIn('GENERAL', log.metadata.get('category', ''))

    def test_audit_masks_integration_secrets(self):
        self.admin_client.patch('/api/v1/admin/settings/INTEGRATIONS/', {
            'settings': {'openrouter': {'api_key': 'super-secret', 'base_url': 'https://x.com'}}
        }, format='json')
        log = UserAuditLog.objects.filter(action='settings_updated').last()
        changes = log.metadata.get('changes', {})
        if 'openrouter' in changes:
            new_val = changes['openrouter'].get('new', {})
            if isinstance(new_val, dict) and 'api_key' in new_val:
                self.assertEqual(new_val['api_key'], '***')

    def test_failed_update_no_audit(self):
        initial = UserAuditLog.objects.filter(action='settings_updated').count()
        self.admin_client.patch('/api/v1/admin/settings/AI/', {
            'settings': {'temperature': 99.0}
        }, format='json')
        self.assertEqual(UserAuditLog.objects.filter(action='settings_updated').count(), initial)


# ═══════════════════════════════════════════════════════════════════
# 7. Seed Command
# ═══════════════════════════════════════════════════════════════════

class SeedCommandTests(BaseSettingsTest):
    def test_seed_creates_settings(self):
        Setting.objects.all().delete()
        out = StringIO()
        call_command('seed_settings', stdout=out)
        output = out.getvalue()
        self.assertIn('Created: 53', output)
        self.assertEqual(Setting.objects.count(), 53)

    def test_seed_idempotent(self):
        Setting.objects.all().delete()
        call_command('seed_settings', stdout=StringIO())
        out = StringIO()
        call_command('seed_settings', stdout=out)
        self.assertIn('Skipped: 53', out.getvalue())

    def test_seed_force_updates(self):
        Setting.objects.all().delete()
        call_command('seed_settings', stdout=StringIO())
        # Change a value
        Setting.objects.filter(key='company_name').update(value='Changed')
        out = StringIO()
        call_command('seed_settings', '--force', stdout=out)
        self.assertIn('Updated: 53', out.getvalue())
        self.assertEqual(Setting.objects.get(category='GENERAL', key='company_name').value, 'B10 IT Solution')

    def test_seed_never_creates_real_secrets(self):
        Setting.objects.all().delete()
        call_command('seed_settings', stdout=StringIO())
        openrouter = Setting.objects.get(category='INTEGRATIONS', key='openrouter')
        self.assertEqual(openrouter.value['api_key'], '')

    def test_seed_public_flags_correct(self):
        Setting.objects.all().delete()
        call_command('seed_settings', stdout=StringIO())
        # GENERAL should be public
        general = Setting.objects.filter(category='GENERAL')
        for s in general:
            self.assertTrue(s.is_public)
        # INTEGRATIONS should not be public
        integrations = Setting.objects.filter(category='INTEGRATIONS')
        for s in integrations:
            self.assertFalse(s.is_public)
