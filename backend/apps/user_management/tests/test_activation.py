"""
Tests for activation, deactivation, and last-superuser protection.

Endpoints:
- POST /api/v1/admin/users/{id}/activate/
- POST /api/v1/admin/users/{id}/deactivate/
- PATCH /api/v1/admin/users/{id}/ (is_active, is_superuser, groups protections)

Covers:
- Successful activation/deactivation
- Self-deactivation prevention
- Last active superuser protection (deactivate, is_superuser=False, remove Admin group)
- is_active=False via PATCH on last superuser (regression)
- 404 for missing users
- Audit log creation on success / no audit on failure
- User record persists after deactivation (soft delete)
"""
from django.contrib.auth import get_user_model

from apps.user_management.models import UserAuditLog
from apps.user_management.tests.conftest import BaseUserManagementTest

User = get_user_model()


class ActivateUserTests(BaseUserManagementTest):
    """Tests for POST /api/v1/admin/users/{id}/activate/"""

    def test_activate_sets_is_active_true(self):
        resp = self.admin_client.post(
            f'/api/v1/admin/users/{self.inactive_user.pk}/activate/'
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data['data']['is_active'])
        # Verify in DB
        self.inactive_user.refresh_from_db()
        self.assertTrue(self.inactive_user.is_active)

    def test_activate_already_active_user_succeeds(self):
        """Activating an already-active user is idempotent."""
        resp = self.admin_client.post(
            f'/api/v1/admin/users/{self.regular_user.pk}/activate/'
        )
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.json()['data']['is_active'])

    def test_activate_nonexistent_returns_404(self):
        resp = self.admin_client.post('/api/v1/admin/users/99999/activate/')
        self.assertEqual(resp.status_code, 404)
        self.assertEqual(resp.json()['code'], 'user_not_found')

    def test_activate_creates_audit_log(self):
        self.admin_client.post(
            f'/api/v1/admin/users/{self.inactive_user.pk}/activate/'
        )
        logs = UserAuditLog.objects.filter(
            target_user=self.inactive_user, action='user_activated'
        )
        self.assertEqual(logs.count(), 1)
        self.assertEqual(logs.first().actor, self.admin_user)

    def test_activate_returns_detail_serializer(self):
        resp = self.admin_client.post(
            f'/api/v1/admin/users/{self.inactive_user.pk}/activate/'
        )
        data = resp.json()['data']
        self.assertIn('permissions', data)
        self.assertIn('groups', data)
        self.assertNotIn('password', data)


class DeactivateUserTests(BaseUserManagementTest):
    """Tests for POST /api/v1/admin/users/{id}/deactivate/"""

    def test_deactivate_sets_is_active_false(self):
        resp = self.admin_client.post(
            f'/api/v1/admin/users/{self.regular_user.pk}/deactivate/'
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertFalse(data['data']['is_active'])
        # Verify in DB
        self.regular_user.refresh_from_db()
        self.assertFalse(self.regular_user.is_active)

    def test_deactivate_user_record_persists(self):
        """Deactivation is soft — user record still exists."""
        self.admin_client.post(
            f'/api/v1/admin/users/{self.regular_user.pk}/deactivate/'
        )
        self.assertTrue(User.objects.filter(pk=self.regular_user.pk).exists())

    def test_deactivate_nonexistent_returns_404(self):
        resp = self.admin_client.post('/api/v1/admin/users/99999/deactivate/')
        self.assertEqual(resp.status_code, 404)
        self.assertEqual(resp.json()['code'], 'user_not_found')

    def test_deactivate_creates_audit_log(self):
        self.admin_client.post(
            f'/api/v1/admin/users/{self.regular_user.pk}/deactivate/'
        )
        logs = UserAuditLog.objects.filter(
            target_user=self.regular_user, action='user_deactivated'
        )
        self.assertEqual(logs.count(), 1)
        self.assertEqual(logs.first().actor, self.admin_user)

    def test_deactivate_returns_detail_serializer(self):
        resp = self.admin_client.post(
            f'/api/v1/admin/users/{self.regular_user.pk}/deactivate/'
        )
        data = resp.json()['data']
        self.assertIn('permissions', data)
        self.assertNotIn('password', data)


class SelfDeactivationProtectionTests(BaseUserManagementTest):
    """Tests for self-deactivation prevention."""

    def test_cannot_deactivate_self(self):
        resp = self.admin_client.post(
            f'/api/v1/admin/users/{self.admin_user.pk}/deactivate/'
        )
        self.assertEqual(resp.status_code, 400)
        data = resp.json()
        self.assertEqual(data['code'], 'cannot_deactivate_self')

    def test_self_deactivation_creates_no_audit_log(self):
        initial_count = UserAuditLog.objects.count()
        self.admin_client.post(
            f'/api/v1/admin/users/{self.admin_user.pk}/deactivate/'
        )
        self.assertEqual(UserAuditLog.objects.count(), initial_count)

    def test_self_deactivation_user_remains_active(self):
        self.admin_client.post(
            f'/api/v1/admin/users/{self.admin_user.pk}/deactivate/'
        )
        self.admin_user.refresh_from_db()
        self.assertTrue(self.admin_user.is_active)


class LastSuperuserProtectionTests(BaseUserManagementTest):
    """
    Tests for last active superuser protection.
    admin_user is the only active superuser in these tests.
    """

    def test_cannot_deactivate_last_superuser(self):
        resp = self.admin_client.post(
            f'/api/v1/admin/users/{self.admin_user.pk}/deactivate/'
        )
        self.assertEqual(resp.status_code, 400)
        # Could be cannot_deactivate_self OR last_superuser_protection
        # (admin is deactivating self, which triggers self-protection first)
        data = resp.json()
        self.assertIn(data['code'], ['cannot_deactivate_self', 'last_superuser_protection'])

    def test_cannot_deactivate_last_superuser_by_another_admin(self):
        """A non-superuser admin cannot deactivate the last superuser."""
        # Make another admin (non-superuser) who can try to deactivate
        other_admin = self.create_user(username='other_admin', email='oa@test.com')
        other_admin.groups.add(self.admin_group)
        from rest_framework.test import APIClient
        from rest_framework_simplejwt.tokens import AccessToken
        other_client = APIClient()
        other_client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {str(AccessToken.for_user(other_admin))}'
        )

        resp = other_client.post(
            f'/api/v1/admin/users/{self.admin_user.pk}/deactivate/'
        )
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.json()['code'], 'last_superuser_protection')

    def test_deactivate_last_superuser_creates_no_audit_log(self):
        """Failed deactivation creates zero audit entries."""
        other_admin = self.create_user(username='other_admin2', email='oa2@test.com')
        other_admin.groups.add(self.admin_group)
        from rest_framework.test import APIClient
        from rest_framework_simplejwt.tokens import AccessToken
        other_client = APIClient()
        other_client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {str(AccessToken.for_user(other_admin))}'
        )

        initial_count = UserAuditLog.objects.count()
        other_client.post(
            f'/api/v1/admin/users/{self.admin_user.pk}/deactivate/'
        )
        self.assertEqual(UserAuditLog.objects.count(), initial_count)

    def test_update_cannot_set_is_superuser_false_on_last(self):
        resp = self.admin_client.patch(
            f'/api/v1/admin/users/{self.admin_user.pk}/',
            {'is_superuser': False},
            format='json',
        )
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.json()['code'], 'last_superuser_protection')

    def test_update_cannot_remove_admin_group_from_last(self):
        resp = self.admin_client.patch(
            f'/api/v1/admin/users/{self.admin_user.pk}/',
            {'groups': ['Support']},  # removes Admin
            format='json',
        )
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.json()['code'], 'invalid_groups')

    def test_update_cannot_set_is_active_false_on_last_superuser(self):
        """Regression: PATCH is_active=False on last superuser must be rejected."""
        resp = self.admin_client.patch(
            f'/api/v1/admin/users/{self.admin_user.pk}/',
            {'is_active': False},
            format='json',
        )
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.json()['code'], 'last_superuser_protection')

    def test_protection_not_triggered_when_multiple_superusers(self):
        """If there are 2+ active superusers, deactivation is allowed."""
        other_super = self.create_user(
            username='other_super', email='os@test.com', is_superuser=True,
        )
        other_super.groups.add(self.admin_group)
        from rest_framework.test import APIClient
        from rest_framework_simplejwt.tokens import AccessToken
        other_client = APIClient()
        other_client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {str(AccessToken.for_user(other_super))}'
        )

        # other_super can deactivate admin_user since there are 2 superusers
        resp = other_client.post(
            f'/api/v1/admin/users/{self.admin_user.pk}/deactivate/'
        )
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(resp.json()['data']['is_active'])

    def test_update_is_superuser_false_allowed_with_multiple(self):
        """With 2+ active superusers, removing one's superuser status is allowed."""
        other_super = self.create_user(
            username='other_super2', email='os2@test.com', is_superuser=True,
        )
        other_super.groups.add(self.admin_group)

        resp = self.admin_client.patch(
            f'/api/v1/admin/users/{other_super.pk}/',
            {'is_superuser': False},
            format='json',
        )
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(resp.json()['data']['is_superuser'])
