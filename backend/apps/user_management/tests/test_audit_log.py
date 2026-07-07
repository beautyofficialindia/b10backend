"""
Tests for the audit logging system.

Endpoint: GET /api/v1/admin/users/{id}/audit-log/

Covers:
- Audit entries created for all mutating operations
- No audit entries for read operations
- No audit entries for failed operations
- actor and target_user correctness
- action values
- metadata safety (no passwords, tokens, secrets)
- created_at ordering (newest first)
- Pagination
- Serializer fields
- 404 for nonexistent user
"""
from django.contrib.auth import get_user_model

from apps.user_management.models import UserAuditLog
from apps.user_management.tests.conftest import BaseUserManagementTest

User = get_user_model()


class AuditLogCreationTests(BaseUserManagementTest):
    """Tests that audit logs are created for every mutating operation."""

    def test_create_user_logs_user_created(self):
        resp = self.admin_client.post('/api/v1/admin/users/', {
            'username': 'audit_create',
            'email': 'ac@test.com',
            'password': 'StrongPass99!',
        }, format='json')
        self.assertEqual(resp.status_code, 201)
        user = User.objects.get(username='audit_create')
        log = UserAuditLog.objects.get(target_user=user, action='user_created')
        self.assertEqual(log.actor, self.admin_user)
        self.assertIn('audit_create', log.description)

    def test_update_user_logs_user_updated(self):
        target = self.create_user(username='audit_update', email='au@test.com')
        self.admin_client.patch(
            f'/api/v1/admin/users/{target.pk}/',
            {'first_name': 'Changed'},
            format='json',
        )
        log = UserAuditLog.objects.get(target_user=target, action='user_updated')
        self.assertEqual(log.actor, self.admin_user)
        self.assertIn('first_name', log.metadata.get('old_values', {}))
        self.assertIn('first_name', log.metadata.get('new_values', {}))

    def test_update_groups_logs_groups_changed(self):
        target = self.create_user(username='audit_groups', email='ag@test.com')
        target.groups.add(self.support_group)
        self.admin_client.patch(
            f'/api/v1/admin/users/{target.pk}/',
            {'groups': ['Sales']},
            format='json',
        )
        log = UserAuditLog.objects.get(target_user=target, action='groups_changed')
        self.assertEqual(log.actor, self.admin_user)
        self.assertIn('groups', log.metadata.get('old_values', {}))
        self.assertIn('groups', log.metadata.get('new_values', {}))

    def test_activate_logs_user_activated(self):
        self.admin_client.post(
            f'/api/v1/admin/users/{self.inactive_user.pk}/activate/'
        )
        log = UserAuditLog.objects.get(
            target_user=self.inactive_user, action='user_activated'
        )
        self.assertEqual(log.actor, self.admin_user)

    def test_deactivate_logs_user_deactivated(self):
        self.admin_client.post(
            f'/api/v1/admin/users/{self.regular_user.pk}/deactivate/'
        )
        log = UserAuditLog.objects.get(
            target_user=self.regular_user, action='user_deactivated'
        )
        self.assertEqual(log.actor, self.admin_user)

    def test_bulk_activate_logs_bulk_activated(self):
        self.admin_client.post('/api/v1/admin/users/bulk-activate/', {
            'user_ids': [self.inactive_user.pk],
        }, format='json')
        log = UserAuditLog.objects.get(
            target_user=self.inactive_user, action='bulk_activated'
        )
        self.assertEqual(log.actor, self.admin_user)

    def test_bulk_deactivate_logs_bulk_deactivated(self):
        target = self.create_user(username='bulk_deact_log', email='bdl@test.com')
        self.admin_client.post('/api/v1/admin/users/bulk-deactivate/', {
            'user_ids': [target.pk],
        }, format='json')
        log = UserAuditLog.objects.get(target_user=target, action='bulk_deactivated')
        self.assertEqual(log.actor, self.admin_user)

    def test_password_reset_logs_password_reset(self):
        target = self.create_user(username='pw_log', email='pwl@test.com')
        self.admin_client.post(
            f'/api/v1/admin/users/{target.pk}/reset-password/',
            {'password': 'NewPass99!'},
            format='json',
        )
        log = UserAuditLog.objects.get(target_user=target, action='password_reset')
        self.assertEqual(log.actor, self.admin_user)


class AuditLogNoCreationTests(BaseUserManagementTest):
    """Tests that read operations and failed mutations create no audit logs."""

    def test_list_creates_no_log(self):
        initial = UserAuditLog.objects.count()
        self.admin_client.get('/api/v1/admin/users/')
        self.assertEqual(UserAuditLog.objects.count(), initial)

    def test_retrieve_creates_no_log(self):
        initial = UserAuditLog.objects.count()
        self.admin_client.get(f'/api/v1/admin/users/{self.admin_user.pk}/')
        self.assertEqual(UserAuditLog.objects.count(), initial)

    def test_me_creates_no_log(self):
        initial = UserAuditLog.objects.count()
        self.admin_client.get('/api/v1/admin/users/me/')
        self.assertEqual(UserAuditLog.objects.count(), initial)

    def test_audit_log_endpoint_creates_no_log(self):
        initial = UserAuditLog.objects.count()
        self.admin_client.get(f'/api/v1/admin/users/{self.admin_user.pk}/audit-log/')
        self.assertEqual(UserAuditLog.objects.count(), initial)

    def test_failed_create_creates_no_log(self):
        initial = UserAuditLog.objects.count()
        self.admin_client.post('/api/v1/admin/users/', {
            'username': 'test_admin',  # duplicate
            'email': 'dup@test.com',
            'password': 'StrongPass99!',
        }, format='json')
        self.assertEqual(UserAuditLog.objects.count(), initial)

    def test_failed_update_creates_no_log(self):
        initial = UserAuditLog.objects.count()
        self.admin_client.patch(
            f'/api/v1/admin/users/{self.regular_user.pk}/',
            {'username': 'rejected'},
            format='json',
        )
        self.assertEqual(UserAuditLog.objects.count(), initial)

    def test_failed_deactivate_creates_no_log(self):
        initial = UserAuditLog.objects.count()
        self.admin_client.post(
            f'/api/v1/admin/users/{self.admin_user.pk}/deactivate/'
        )
        self.assertEqual(UserAuditLog.objects.count(), initial)

    def test_failed_password_reset_creates_no_log(self):
        target = self.create_user(username='fpw', email='fpw@test.com')
        initial = UserAuditLog.objects.count()
        self.admin_client.post(
            f'/api/v1/admin/users/{target.pk}/reset-password/',
            {'password': '123'},  # weak
            format='json',
        )
        self.assertEqual(UserAuditLog.objects.count(), initial)


class AuditLogMetadataSafetyTests(BaseUserManagementTest):
    """Tests that metadata never contains secrets."""

    def test_create_metadata_no_password(self):
        self.admin_client.post('/api/v1/admin/users/', {
            'username': 'safe_create',
            'email': 'sc@test.com',
            'password': 'SecretPass99!',
        }, format='json')
        user = User.objects.get(username='safe_create')
        log = UserAuditLog.objects.get(target_user=user, action='user_created')
        full_str = str(log.metadata) + str(log.description)
        self.assertNotIn('SecretPass99!', full_str)

    def test_password_reset_metadata_no_password(self):
        target = self.create_user(username='safe_pw', email='sp@test.com')
        self.admin_client.post(
            f'/api/v1/admin/users/{target.pk}/reset-password/',
            {'password': 'TopSecret88!'},
            format='json',
        )
        log = UserAuditLog.objects.get(target_user=target, action='password_reset')
        full_str = str(log.metadata) + str(log.description)
        self.assertNotIn('TopSecret88!', full_str)

    def test_update_metadata_no_password_hash(self):
        target = self.create_user(username='safe_upd', email='su@test.com')
        self.admin_client.patch(
            f'/api/v1/admin/users/{target.pk}/',
            {'first_name': 'Safe'},
            format='json',
        )
        log = UserAuditLog.objects.get(target_user=target, action='user_updated')
        full_str = str(log.metadata)
        self.assertNotIn('pbkdf2_sha256', full_str)


class AuditLogEndpointTests(BaseUserManagementTest):
    """Tests for GET /api/v1/admin/users/{id}/audit-log/"""

    def setUp(self):
        super().setUp()
        self.target = self.create_user(username='log_target', email='lt@test.com')
        # Create some audit entries
        self.admin_client.post(
            f'/api/v1/admin/users/{self.target.pk}/activate/'
        )
        self.admin_client.patch(
            f'/api/v1/admin/users/{self.target.pk}/',
            {'first_name': 'Logged'},
            format='json',
        )

    def test_audit_log_endpoint_returns_entries(self):
        resp = self.admin_client.get(
            f'/api/v1/admin/users/{self.target.pk}/audit-log/'
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data['success'])
        self.assertGreater(len(data['data']), 0)

    def test_audit_log_ordered_newest_first(self):
        resp = self.admin_client.get(
            f'/api/v1/admin/users/{self.target.pk}/audit-log/'
        )
        entries = resp.json()['data']
        timestamps = [e['created_at'] for e in entries]
        self.assertEqual(timestamps, sorted(timestamps, reverse=True))

    def test_audit_log_serializer_fields(self):
        resp = self.admin_client.get(
            f'/api/v1/admin/users/{self.target.pk}/audit-log/'
        )
        entries = resp.json()['data']
        expected_fields = {
            'id', 'actor', 'actor_username', 'target_user',
            'action', 'description', 'metadata', 'created_at',
        }
        for entry in entries:
            self.assertEqual(set(entry.keys()), expected_fields)

    def test_audit_log_actor_username_populated(self):
        resp = self.admin_client.get(
            f'/api/v1/admin/users/{self.target.pk}/audit-log/'
        )
        entries = resp.json()['data']
        for entry in entries:
            self.assertEqual(entry['actor_username'], 'test_admin')

    def test_audit_log_target_user_matches(self):
        resp = self.admin_client.get(
            f'/api/v1/admin/users/{self.target.pk}/audit-log/'
        )
        entries = resp.json()['data']
        for entry in entries:
            self.assertEqual(entry['target_user'], self.target.pk)

    def test_audit_log_nonexistent_user_returns_404(self):
        resp = self.admin_client.get('/api/v1/admin/users/99999/audit-log/')
        self.assertEqual(resp.status_code, 404)
        self.assertEqual(resp.json()['code'], 'user_not_found')

    def test_audit_log_pagination(self):
        resp = self.admin_client.get(
            f'/api/v1/admin/users/{self.target.pk}/audit-log/?page_size=1'
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        meta = data['meta']['pagination']
        self.assertEqual(meta['page_size'], 1)
        self.assertEqual(len(data['data']), 1)
        self.assertGreaterEqual(meta['total_count'], 2)

    def test_audit_log_page_2(self):
        resp = self.admin_client.get(
            f'/api/v1/admin/users/{self.target.pk}/audit-log/?page_size=1&page=2'
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data['meta']['pagination']['page'], 2)

    def test_audit_log_empty_for_user_with_no_actions(self):
        """A user with no audit entries returns empty list."""
        new_user = self.create_user(username='no_logs', email='nl@test.com')
        resp = self.admin_client.get(
            f'/api/v1/admin/users/{new_user.pk}/audit-log/'
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(len(data['data']), 0)

    def test_audit_log_does_not_return_other_users_logs(self):
        """Audit log endpoint only returns logs for the specified user."""
        other = self.create_user(username='other_log', email='ol@test.com')
        # Create a log for 'other'
        self.admin_client.post(
            f'/api/v1/admin/users/{other.pk}/activate/'
        )
        # Query target's log — should not include other's entry
        resp = self.admin_client.get(
            f'/api/v1/admin/users/{self.target.pk}/audit-log/'
        )
        entries = resp.json()['data']
        for entry in entries:
            self.assertNotEqual(entry['target_user'], other.pk)
