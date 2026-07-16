from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission

from .models import PlatformSetting
from .constants import SettingGroup, ValueType

User = get_user_model()

class PlatformSettingsAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='admin', password='password', is_staff=True, is_superuser=True)
        self.client.force_authenticate(user=self.user)
        
        self.setting_normal = PlatformSetting.objects.create(
            group=SettingGroup.GENERAL,
            key='NORMAL_KEY',
            value='normal_value',
            value_type=ValueType.STRING,
            is_sensitive=False,
            display_name='Normal Key',
            description='This is normal'
        )
        
        self.setting_sensitive = PlatformSetting.objects.create(
            group=SettingGroup.SECURITY,
            key='SECRET_KEY',
            value='super_secret',
            value_type=ValueType.STRING,
            is_sensitive=True,
            display_name='Secret Key',
            description='This is sensitive'
        )

    def test_list_settings_masks_sensitive_values(self):
        url = reverse('settings-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        results = response.data['data']
        self.assertEqual(len(results), 2)
        
        for item in results:
            if item['key'] == 'SECRET_KEY':
                self.assertEqual(item['value'], '********')
            else:
                self.assertEqual(item['value'], 'normal_value')

    def test_search_settings_excludes_value(self):
        url = reverse('settings-list')
        
        # Search for key matches
        response = self.client.get(f"{url}?search=SECRET")
        self.assertEqual(len(response.data['data']), 1)
        
        # Search for description matches
        response = self.client.get(f"{url}?search=normal")
        self.assertEqual(len(response.data['data']), 1)
        
        # Search for value should NOT match (because value is not in search_fields)
        response = self.client.get(f"{url}?search=super_secret")
        self.assertEqual(len(response.data['data']), 0)

    def test_group_counts(self):
        url = reverse('settings-groups')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        groups = response.data
        self.assertEqual(len(groups), 2)
        
        for group in groups:
            if group['name'] == SettingGroup.GENERAL:
                self.assertEqual(group['count'], 1)
                self.assertEqual(group['editable_count'], 1)

    def test_update_setting_only_allows_value(self):
        url = reverse('settings-detail', args=[self.setting_normal.id])
        
        # Attempt to update value and description
        data = {
            'value': 'updated_value',
            'description': 'hacked description',
            'is_sensitive': True
        }
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.setting_normal.refresh_from_db()
        self.assertEqual(self.setting_normal.value, 'updated_value')
        self.assertEqual(self.setting_normal.description, 'This is normal') # Unchanged
        self.assertFalse(self.setting_normal.is_sensitive) # Unchanged

    def test_update_sensitive_setting_masks_response(self):
        url = reverse('settings-detail', args=[self.setting_sensitive.id])
        
        data = {
            'value': 'new_super_secret'
        }
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.assertEqual(response.data['value'], '********')
        
        self.setting_sensitive.refresh_from_db()
        self.assertEqual(self.setting_sensitive.value, 'new_super_secret')

    def test_reset_fails_with_invalid_token(self):
        url = reverse('settings-reset')
        
        # Empty body
        response = self.client.post(url, {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Invalid confirm string
        response = self.client.post(url, {'confirm': 'yes'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Valid confirm string
        response = self.client.post(url, {'confirm': 'RESET_PLATFORM_SETTINGS'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_cache_endpoints(self):
        clear_url = reverse('settings-cache-clear')
        refresh_url = reverse('settings-cache-refresh')
        
        # Empty payload clears all
        response = self.client.post(clear_url, {})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('Global cache cleared', response.data['message'])
        
        # Group payload
        response = self.client.post(clear_url, {'group': SettingGroup.AI})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('group AI', response.data['message'])
        
        # Refresh specific key
        response = self.client.post(refresh_url, {'group': SettingGroup.GENERAL, 'key': 'NORMAL_KEY'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('NORMAL_KEY', response.data['message'])
