"""Shared test fixtures for role_management app."""
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from rest_framework.test import APITestCase, APIClient
from rest_framework_simplejwt.tokens import AccessToken

User = get_user_model()


class BaseRoleManagementTest(APITestCase):
    def setUp(self):
        super().setUp()
        self.admin_group = Group.objects.create(name='Admin')
        self.sales_group = Group.objects.create(name='Sales')
        self.support_group = Group.objects.create(name='Support')

        self.admin_user = User.objects.create_superuser(
            username='role_admin', email='roleadmin@test.com', password='AdminPass123!',
        )
        self.admin_user.groups.add(self.admin_group)

        self.regular_user = User.objects.create_user(
            username='role_regular', email='rolereg@test.com', password='RegPass123!', is_staff=True,
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

    def get_permission_codename(self):
        """Return a valid 'app_label.codename' string."""
        perm = Permission.objects.first()
        return f"{perm.content_type.app_label}.{perm.codename}"
