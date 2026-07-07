"""
Shared test fixtures for the user_management app.

Usage in test files:
    from apps.user_management.tests.conftest import BaseUserManagementTest
"""
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from rest_framework.test import APITestCase, APIClient
from rest_framework_simplejwt.tokens import AccessToken

User = get_user_model()


class BaseUserManagementTest(APITestCase):
    """
    Base test class providing shared fixtures for all user_management tests.

    Fixtures created in setUp:
        - self.admin_group: Group named 'Admin'
        - self.support_group: Group named 'Support'
        - self.sales_group: Group named 'Sales'
        - self.admin_user: Superuser in Admin group (the "actor")
        - self.regular_user: Authenticated user, NOT in Admin group
        - self.inactive_user: User with is_active=False
        - self.admin_client: APIClient authenticated as admin_user
        - self.regular_client: APIClient authenticated as regular_user
        - self.anon_client: APIClient with no credentials
    """

    def setUp(self):
        super().setUp()

        # Groups
        self.admin_group = Group.objects.create(name='Admin')
        self.support_group = Group.objects.create(name='Support')
        self.sales_group = Group.objects.create(name='Sales')

        # Admin user (superuser + Admin group)
        self.admin_user = User.objects.create_superuser(
            username='test_admin',
            email='admin@test.com',
            password='AdminPass123!',
            first_name='Admin',
            last_name='User',
        )
        self.admin_user.groups.add(self.admin_group)

        # Regular authenticated user (not in Admin group)
        self.regular_user = User.objects.create_user(
            username='test_regular',
            email='regular@test.com',
            password='RegularPass123!',
            first_name='Regular',
            last_name='User',
            is_staff=True,
        )
        self.regular_user.groups.add(self.support_group)

        # Inactive user
        self.inactive_user = User.objects.create_user(
            username='test_inactive',
            email='inactive@test.com',
            password='InactivePass123!',
            first_name='Inactive',
            last_name='User',
            is_active=False,
        )

        # API Clients
        self.admin_client = APIClient()
        admin_token = str(AccessToken.for_user(self.admin_user))
        self.admin_client.credentials(HTTP_AUTHORIZATION=f'Bearer {admin_token}')

        self.regular_client = APIClient()
        regular_token = str(AccessToken.for_user(self.regular_user))
        self.regular_client.credentials(HTTP_AUTHORIZATION=f'Bearer {regular_token}')

        self.anon_client = APIClient()

    def create_user(self, username='extra_user', email='extra@test.com', **kwargs):
        """Helper to create additional users for tests."""
        defaults = {
            'password': 'ExtraPass123!',
            'first_name': 'Extra',
            'last_name': 'User',
            'is_staff': True,
            'is_active': True,
        }
        defaults.update(kwargs)
        password = defaults.pop('password')
        user = User.objects.create_user(username=username, email=email, password=password, **defaults)
        return user
