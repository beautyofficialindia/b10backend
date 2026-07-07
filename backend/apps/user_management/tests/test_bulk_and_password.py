"""
Tests for bulk operations and password reset.

Endpoints:
- POST /api/v1/admin/users/bulk-activate/
- POST /api/v1/admin/users/bulk-deactivate/
- POST /api/v1/admin/users/{id}/reset-password/

Covers:
- Bulk activate: multiple users, skip already active, skip missing, counts, audit
- Bulk deactivate: multiple users, skip inactive, skip self, skip last superuser,
  skip missing, counts, audit
- Password reset: valid, weak, hashing, audit, missing password, nonexistent user
- No plaintext password in responses or audit metadata
"""
from django.contrib.auth import get_user_model

from apps.user_management.models import UserAuditLog
from apps.user_management.tests.conftest import BaseUserManagementTest

User = get_user_model()


class BulkActivateTests(BaseUserManagementTest):
    """Tests for POST /api/v1/admin/users/bulk-activate/"""

    def setUp(self):
        super().setUp()
        self.inactive1 = self.create_user(
            username='inactive1', email='i1@test.com', is_active=False,
        )
        self.inactive2 = self.create_user(
            username='inactive2', email='i2@test.com', is_active=False,
        )
        self.active_user = self.create_user(
            username='already_active', email='aa@test.com', is_active=True,
        )

    def test_bulk_activate_multiple_users(self):
        resp = self.admin_client.post('/api/v1/admin/users/bulk-activate/', {
            'user_ids': [self.inactive1.pk, self.inactive2.pk],
        }, format='json')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()['data']
        self.assertEqual(data['activated_count'], 2)
        self.assertEqual(len(data['skipped']), 0)
        # Verify in DB
        self.inactive1.refresh_from_db()
        self.inactive2.refresh_from_db()
        self.assertTrue(self.inactive1.is_active)
        self.assertTrue(self.inactive2.is_active)

    def test_bulk_activate_skips_already_active(self):
        resp = self.admin_client.post('/api/v1/admin/users/bulk-activate/', {
            'user_ids': [self.active_user.pk],
        }, format='json')
        data = resp.json()['data']
        self.assertEqual(data['activated_count'], 0)
        self.assertEqual(len(data['skipped']), 1)
        self.assertEqual(data['skipped'][0]['reason'], 'already active')

    def test_bulk_activate_skips_missing_ids(self):
        resp = self.admin_client.post('/api/v1/admin/users/bulk-activate/', {
            'user_ids': [99999, 88888],
        }, format='json')
        data = resp.json()['data']
        self.assertEqual(data['activated_count'], 0)
        self.assertEqual(len(data['skipped']), 2)
        for s in data['skipped']:
            self.assertEqual(s['reason'], 'user not found')

    def test_bulk_activate_mixed_results(self):
        """Mix of inactive, active, and missing IDs."""
        resp = self.admin_client.post('/api/v1/admin/users/bulk-activate/', {
            'user_ids': [self.inactive1.pk, self.active_user.pk, 99999],
        }, format='json')
        data = resp.json()['data']
        self.assertEqual(data['activated_count'], 1)
        self.assertEqual(len(data['skipped']), 2)

    def test_bulk_activate_summary_counts_consistent(self):
        """activated_count + len(skipped) == len(input_ids)"""
        ids = [self.inactive1.pk, self.inactive2.pk, self.active_user.pk, 99999]
        resp = self.admin_client.post('/api/v1/admin/users/bulk-activate/', {
            'user_ids': ids,
        }, format='json')
        data = resp.json()['data']
        self.assertEqual(data['activated_count'] + len(data['skipped']), len(ids))

    def test_bulk_activate_creates_audit_logs_only_for_success(self):
        """Audit logs created only for actually-activated users."""
        initial_count = UserAuditLog.objects.filter(action='bulk_activated').count()
        self.admin_client.post('/api/v1/admin/users/bulk-activate/', {
            'user_ids': [self.inactive1.pk, self.active_user.pk, 99999],
        }, format='json')
        new_logs = UserAuditLog.objects.filter(action='bulk_activated').count() - initial_count
        self.assertEqual(new_logs, 1)  # Only inactive1 was activated

    def test_bulk_activate_empty_list_returns_400(self):
        resp = self.admin_client.post('/api/v1/admin/users/bulk-activate/', {
            'user_ids': [],
        }, format='json')
        self.assertEqual(resp.status_code, 400)


class BulkDeactivateTests(BaseUserManagementTest):
    """Tests for POST /api/v1/admin/users/bulk-deactivate/"""

    def setUp(self):
        super().setUp()
        self.target1 = self.create_user(username='target1', email='t1@test.com', is_active=True)
        self.target2 = self.create_user(username='target2', email='t2@test.com', is_active=True)
        self.already_inactive = self.create_user(
            username='already_inactive', email='ai@test.com', is_active=False,
        )

    def test_bulk_deactivate_multiple_users(self):
        resp = self.admin_client.post('/api/v1/admin/users/bulk-deactivate/', {
            'user_ids': [self.target1.pk, self.target2.pk],
        }, format='json')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()['data']
        self.assertEqual(data['deactivated_count'], 2)
        self.assertEqual(len(data['skipped']), 0)
        self.target1.refresh_from_db()
        self.target2.refresh_from_db()
        self.assertFalse(self.target1.is_active)
        self.assertFalse(self.target2.is_active)

    def test_bulk_deactivate_skips_already_inactive(self):
        resp = self.admin_client.post('/api/v1/admin/users/bulk-deactivate/', {
            'user_ids': [self.already_inactive.pk],
        }, format='json')
        data = resp.json()['data']
        self.assertEqual(data['deactivated_count'], 0)
        self.assertEqual(len(data['skipped']), 1)
        self.assertEqual(data['skipped'][0]['reason'], 'already inactive')

    def test_bulk_deactivate_skips_self(self):
        resp = self.admin_client.post('/api/v1/admin/users/bulk-deactivate/', {
            'user_ids': [self.admin_user.pk],
        }, format='json')
        data = resp.json()['data']
        self.assertEqual(data['deactivated_count'], 0)
        skipped_reasons = [s['reason'] for s in data['skipped']]
        self.assertIn('cannot deactivate yourself', skipped_reasons)

    def test_bulk_deactivate_skips_last_superuser(self):
        """Another admin (non-superuser) tries to bulk-deactivate the last superuser."""
        other_admin = self.create_user(username='other_admin_bd', email='oabd@test.com')
        other_admin.groups.add(self.admin_group)
        from rest_framework.test import APIClient
        from rest_framework_simplejwt.tokens import AccessToken
        other_client = APIClient()
        other_client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {str(AccessToken.for_user(other_admin))}'
        )

        resp = other_client.post('/api/v1/admin/users/bulk-deactivate/', {
            'user_ids': [self.admin_user.pk],
        }, format='json')
        data = resp.json()['data']
        self.assertEqual(data['deactivated_count'], 0)
        skipped_reasons = [s['reason'] for s in data['skipped']]
        self.assertIn('cannot deactivate last active superuser', skipped_reasons)

    def test_bulk_deactivate_skips_missing_ids(self):
        resp = self.admin_client.post('/api/v1/admin/users/bulk-deactivate/', {
            'user_ids': [99999],
        }, format='json')
        data = resp.json()['data']
        self.assertEqual(data['deactivated_count'], 0)
        self.assertEqual(data['skipped'][0]['reason'], 'user not found')

    def test_bulk_deactivate_mixed_results(self):
        """Mix of valid targets, self, inactive, missing."""
        resp = self.admin_client.post('/api/v1/admin/users/bulk-deactivate/', {
            'user_ids': [
                self.target1.pk,        # should deactivate
                self.admin_user.pk,     # self - skip
                self.already_inactive.pk,  # already inactive - skip
                99999,                  # missing - skip
            ],
        }, format='json')
        data = resp.json()['data']
        self.assertEqual(data['deactivated_count'], 1)
        self.assertEqual(len(data['skipped']), 3)

    def test_bulk_deactivate_summary_counts_consistent(self):
        """deactivated_count + len(skipped) == len(input_ids)"""
        ids = [self.target1.pk, self.target2.pk, self.admin_user.pk, 99999]
        resp = self.admin_client.post('/api/v1/admin/users/bulk-deactivate/', {
            'user_ids': ids,
        }, format='json')
        data = resp.json()['data']
        self.assertEqual(data['deactivated_count'] + len(data['skipped']), len(ids))

    def test_bulk_deactivate_creates_audit_logs_only_for_success(self):
        """Audit logs created only for actually-deactivated users."""
        initial_count = UserAuditLog.objects.filter(action='bulk_deactivated').count()
        self.admin_client.post('/api/v1/admin/users/bulk-deactivate/', {
            'user_ids': [self.target1.pk, self.admin_user.pk, 99999],
        }, format='json')
        new_logs = UserAuditLog.objects.filter(action='bulk_deactivated').count() - initial_count
        self.assertEqual(new_logs, 1)  # Only target1

    def test_bulk_deactivate_empty_list_returns_400(self):
        resp = self.admin_client.post('/api/v1/admin/users/bulk-deactivate/', {
            'user_ids': [],
        }, format='json')
        self.assertEqual(resp.status_code, 400)


class PasswordResetTests(BaseUserManagementTest):
    """Tests for POST /api/v1/admin/users/{id}/reset-password/"""

    def setUp(self):
        super().setUp()
        self.target = self.create_user(username='pw_target', email='pwt@test.com')

    def test_reset_password_valid(self):
        resp = self.admin_client.post(
            f'/api/v1/admin/users/{self.target.pk}/reset-password/',
            {'password': 'NewStrongPass99!'},
            format='json',
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data['success'])

    def test_reset_password_actually_changes(self):
        """The password is actually changed and verifiable."""
        old_hash = self.target.password
        self.admin_client.post(
            f'/api/v1/admin/users/{self.target.pk}/reset-password/',
            {'password': 'BrandNewPass88!'},
            format='json',
        )
        self.target.refresh_from_db()
        self.assertNotEqual(self.target.password, old_hash)
        self.assertTrue(self.target.check_password('BrandNewPass88!'))

    def test_reset_password_is_hashed(self):
        """The stored password is not plaintext."""
        self.admin_client.post(
            f'/api/v1/admin/users/{self.target.pk}/reset-password/',
            {'password': 'HashedPass77!'},
            format='json',
        )
        self.target.refresh_from_db()
        self.assertNotEqual(self.target.password, 'HashedPass77!')
        self.assertTrue(self.target.password.startswith('pbkdf2_sha256$'))

    def test_reset_password_weak_returns_400(self):
        resp = self.admin_client.post(
            f'/api/v1/admin/users/{self.target.pk}/reset-password/',
            {'password': '123'},
            format='json',
        )
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.json()['code'], 'password_invalid')

    def test_reset_password_common_returns_400(self):
        resp = self.admin_client.post(
            f'/api/v1/admin/users/{self.target.pk}/reset-password/',
            {'password': 'password123'},
            format='json',
        )
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.json()['code'], 'password_invalid')

    def test_reset_password_missing_field_returns_400(self):
        resp = self.admin_client.post(
            f'/api/v1/admin/users/{self.target.pk}/reset-password/',
            {},
            format='json',
        )
        self.assertEqual(resp.status_code, 400)

    def test_reset_password_nonexistent_user_returns_404(self):
        resp = self.admin_client.post(
            '/api/v1/admin/users/99999/reset-password/',
            {'password': 'StrongPass99!'},
            format='json',
        )
        self.assertEqual(resp.status_code, 404)
        self.assertEqual(resp.json()['code'], 'user_not_found')

    def test_reset_password_creates_audit_log(self):
        self.admin_client.post(
            f'/api/v1/admin/users/{self.target.pk}/reset-password/',
            {'password': 'AuditedPass66!'},
            format='json',
        )
        logs = UserAuditLog.objects.filter(
            target_user=self.target, action='password_reset'
        )
        self.assertEqual(logs.count(), 1)
        self.assertEqual(logs.first().actor, self.admin_user)

    def test_reset_password_audit_metadata_has_no_plaintext(self):
        """Audit log metadata must not contain the plaintext password."""
        self.admin_client.post(
            f'/api/v1/admin/users/{self.target.pk}/reset-password/',
            {'password': 'SecretPass55!'},
            format='json',
        )
        log = UserAuditLog.objects.filter(
            target_user=self.target, action='password_reset'
        ).first()
        metadata_str = str(log.metadata)
        self.assertNotIn('SecretPass55!', metadata_str)
        description_str = str(log.description)
        self.assertNotIn('SecretPass55!', description_str)

    def test_reset_password_response_has_no_plaintext(self):
        """API response must not contain the password."""
        resp = self.admin_client.post(
            f'/api/v1/admin/users/{self.target.pk}/reset-password/',
            {'password': 'ResponseCheck44!'},
            format='json',
        )
        response_str = resp.content.decode()
        self.assertNotIn('ResponseCheck44!', response_str)
        self.assertNotIn('password', resp.json().get('data', {}))

    def test_reset_password_failed_creates_no_audit(self):
        """Failed password reset (weak password) creates no audit log."""
        initial_count = UserAuditLog.objects.filter(action='password_reset').count()
        self.admin_client.post(
            f'/api/v1/admin/users/{self.target.pk}/reset-password/',
            {'password': '123'},
            format='json',
        )
        self.assertEqual(
            UserAuditLog.objects.filter(action='password_reset').count(),
            initial_count,
        )
