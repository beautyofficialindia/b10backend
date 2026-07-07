"""Shared test fixtures for settings_management app."""
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from rest_framework.test import APITestCase, APIClient
from rest_framework_simplejwt.tokens import AccessToken

from apps.settings_management.models import Setting

User = get_user_model()


class BaseSettingsTest(APITestCase):
    def setUp(self):
        super().setUp()
        self.admin_group = Group.objects.create(name='Admin')
        self.admin_user = User.objects.create_superuser(
            username='settings_admin', email='sa@test.com', password='AdminPass123!',
        )
        self.admin_user.groups.add(self.admin_group)

        self.regular_user = User.objects.create_user(
            username='settings_reg', email='sr@test.com', password='RegPass123!',
        )

        self.admin_client = APIClient()
        self.admin_client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {str(AccessToken.for_user(self.admin_user))}'
        )
        self.regular_client = APIClient()
        self.regular_client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {str(AccessToken.for_user(self.regular_user))}'
        )
        self.anon_client = APIClient()

        # Seed some test settings
        Setting.objects.create(category='GENERAL', key='company_name', value='TestCo', is_public=True)
        Setting.objects.create(category='GENERAL', key='timezone', value='UTC', is_public=True)
        Setting.objects.create(category='BRANDING', key='primary_color', value='#000', is_public=True)
        Setting.objects.create(category='AI', key='temperature', value=0.7, is_public=False)
        Setting.objects.create(category='AI', key='model', value='gpt-4', is_public=False)
        Setting.objects.create(category='INTEGRATIONS', key='openrouter', value={'api_key': 'sk-secret-123', 'base_url': 'https://api.openrouter.ai'}, is_public=False)
        Setting.objects.create(category='INTEGRATIONS', key='smtp', value={'host': 'smtp.test.com', 'password': 'secret'}, is_public=False)
        Setting.objects.create(category='SECURITY', key='jwt_access_lifetime', value=15, is_public=False)
        Setting.objects.create(category='FEATURE_FLAGS', key='analytics_enabled', value=True, is_public=True)
