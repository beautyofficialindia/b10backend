"""
Tests for CRUD endpoints:
- GET /api/v1/admin/users/{id}/  (retrieve)
- POST /api/v1/admin/users/      (create)
- PATCH /api/v1/admin/users/{id}/ (partial_update)
- GET /api/v1/admin/users/me/     (me)

Covers:
- Successful creation with valid data
- Duplicate username (case-insensitive)
- Duplicate email (case-insensitive)
- Invalid group names
- Weak password rejection
- Email normalization
- Username immutability
- Partial updates
- Group replacement
- 404 for missing users
- Serializer response correctness
- Password hashing verification
- Audit log creation on state changes
"""
from django.contrib.auth import get_user_model

from apps.user_management.models import UserAuditLog
from apps.user_management.tests.conftest import BaseUserManagementTest

User = get_user_model()


class RetrieveUserTests(BaseUserManagementTest):
    """Tests for GET /api/v1/admin/users/{id}/"""

    def test_retrieve_existing_user(self):
        resp = self.admin_client.get(f'/api/v1/admin/users/{self.regular_user.pk}/')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['data']['username'], 'test_regular')

    def test_retrieve_returns_detail_serializer_fields(self):
        resp = self.admin_client.get(f'/api/v1/admin/users/{self.admin_user.pk}/')
        data = resp.json()['data']
        expected_fields = {
            'id', 'username', 'email', 'first_name', 'last_name',
            'is_active', 'is_staff', 'is_superuser', 'groups',
            'date_joined', 'last_login', 'permissions',
        }
        self.assertEqual(set(data.keys()), expected_fields)

    def test_retrieve_includes_permissions(self):
        resp = self.admin_client.get(f'/api/v1/admin/users/{self.admin_user.pk}/')
        data = resp.json()['data']
        self.assertIsInstance(data['permissions'], list)

    def test_retrieve_includes_groups_as_strings(self):
        resp = self.admin_client.get(f'/api/v1/admin/users/{self.regular_user.pk}/')
        data = resp.json()['data']
        self.assertIn('Support', data['groups'])

    def test_retrieve_nonexistent_returns_404(self):
        resp = self.admin_client.get('/api/v1/admin/users/99999/')
        self.assertEqual(resp.status_code, 404)
        data = resp.json()
        self.assertEqual(data['code'], 'user_not_found')

    def test_retrieve_does_not_include_password(self):
        resp = self.admin_client.get(f'/api/v1/admin/users/{self.admin_user.pk}/')
        self.assertNotIn('password', resp.json()['data'])


class MeEndpointTests(BaseUserManagementTest):
    """Tests for GET /api/v1/admin/users/me/"""

    def test_me_returns_current_admin(self):
        resp = self.admin_client.get('/api/v1/admin/users/me/')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()['data']
        self.assertEqual(data['username'], 'test_admin')
        self.assertEqual(data['email'], 'admin@test.com')

    def test_me_returns_detail_serializer(self):
        resp = self.admin_client.get('/api/v1/admin/users/me/')
        data = resp.json()['data']
        self.assertIn('permissions', data)
        self.assertIn('groups', data)


class CreateUserTests(BaseUserManagementTest):
    """Tests for POST /api/v1/admin/users/"""

    def test_create_with_valid_data(self):
        resp = self.admin_client.post('/api/v1/admin/users/', {
            'username': 'brandnew',
            'email': 'brandnew@test.com',
            'password': 'StrongPass99!',
            'first_name': 'Brand',
            'last_name': 'New',
            'groups': ['Support'],
        }, format='json')
        self.assertEqual(resp.status_code, 201)
        data = resp.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['data']['username'], 'brandnew')
        self.assertEqual(data['data']['email'], 'brandnew@test.com')
        self.assertIn('Support', data['data']['groups'])
        self.assertIn('permissions', data['data'])

    def test_create_defaults_is_active_true(self):
        resp = self.admin_client.post('/api/v1/admin/users/', {
            'username': 'activedefault',
            'email': 'ad@test.com',
            'password': 'StrongPass99!',
        }, format='json')
        self.assertEqual(resp.status_code, 201)
        self.assertTrue(resp.json()['data']['is_active'])

    def test_create_with_empty_groups(self):
        resp = self.admin_client.post('/api/v1/admin/users/', {
            'username': 'nogroups',
            'email': 'ng@test.com',
            'password': 'StrongPass99!',
            'groups': [],
        }, format='json')
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(resp.json()['data']['groups'], [])

    def test_create_email_normalized_to_lowercase(self):
        resp = self.admin_client.post('/api/v1/admin/users/', {
            'username': 'emailnorm',
            'email': 'UPPER@CASE.COM',
            'password': 'StrongPass99!',
        }, format='json')
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(resp.json()['data']['email'], 'upper@case.com')

    def test_create_password_is_hashed(self):
        resp = self.admin_client.post('/api/v1/admin/users/', {
            'username': 'hashtest',
            'email': 'ht@test.com',
            'password': 'StrongPass99!',
        }, format='json')
        self.assertEqual(resp.status_code, 201)
        user = User.objects.get(username='hashtest')
        self.assertTrue(user.check_password('StrongPass99!'))
        # Raw password should not be stored
        self.assertNotEqual(user.password, 'StrongPass99!')

    def test_create_does_not_return_password(self):
        resp = self.admin_client.post('/api/v1/admin/users/', {
            'username': 'nopw',
            'email': 'nopw@test.com',
            'password': 'StrongPass99!',
        }, format='json')
        self.assertNotIn('password', resp.json()['data'])

    def test_create_duplicate_username_returns_400(self):
        resp = self.admin_client.post('/api/v1/admin/users/', {
            'username': 'TEST_ADMIN',  # case-insensitive duplicate
            'email': 'unique@test.com',
            'password': 'StrongPass99!',
        }, format='json')
        self.assertEqual(resp.status_code, 400)
        data = resp.json()
        self.assertEqual(data['code'], 'username_exists')

    def test_create_duplicate_email_returns_400(self):
        resp = self.admin_client.post('/api/v1/admin/users/', {
            'username': 'uniqueuser',
            'email': 'ADMIN@TEST.COM',  # case-insensitive duplicate
            'password': 'StrongPass99!',
        }, format='json')
        self.assertEqual(resp.status_code, 400)
        data = resp.json()
        self.assertEqual(data['code'], 'email_exists')

    def test_create_invalid_group_returns_400(self):
        resp = self.admin_client.post('/api/v1/admin/users/', {
            'username': 'badgroup',
            'email': 'bg@test.com',
            'password': 'StrongPass99!',
            'groups': ['NonExistent', 'AlsoFake'],
        }, format='json')
        self.assertEqual(resp.status_code, 400)
        data = resp.json()
        self.assertEqual(data['code'], 'invalid_groups')
        # Should list invalid names
        self.assertIn('NonExistent', data['message'])

    def test_create_partially_invalid_groups_rejects_entirely(self):
        """If any group is invalid, no user is created."""
        resp = self.admin_client.post('/api/v1/admin/users/', {
            'username': 'partialgroup',
            'email': 'pg@test.com',
            'password': 'StrongPass99!',
            'groups': ['Admin', 'FakeGroup'],
        }, format='json')
        self.assertEqual(resp.status_code, 400)
        self.assertFalse(User.objects.filter(username='partialgroup').exists())

    def test_create_weak_password_returns_400(self):
        resp = self.admin_client.post('/api/v1/admin/users/', {
            'username': 'weakpw',
            'email': 'weak@test.com',
            'password': '123',
        }, format='json')
        self.assertEqual(resp.status_code, 400)
        data = resp.json()
        self.assertEqual(data['code'], 'password_invalid')

    def test_create_common_password_returns_400(self):
        resp = self.admin_client.post('/api/v1/admin/users/', {
            'username': 'commonpw',
            'email': 'common@test.com',
            'password': 'password123',
        }, format='json')
        self.assertEqual(resp.status_code, 400)
        data = resp.json()
        self.assertEqual(data['code'], 'password_invalid')

    def test_create_numeric_only_password_returns_400(self):
        resp = self.admin_client.post('/api/v1/admin/users/', {
            'username': 'numericpw',
            'email': 'numeric@test.com',
            'password': '123456789012',
        }, format='json')
        self.assertEqual(resp.status_code, 400)
        data = resp.json()
        self.assertEqual(data['code'], 'password_invalid')

    def test_create_missing_username_returns_400(self):
        resp = self.admin_client.post('/api/v1/admin/users/', {
            'email': 'no_username@test.com',
            'password': 'StrongPass99!',
        }, format='json')
        self.assertEqual(resp.status_code, 400)

    def test_create_missing_email_returns_400(self):
        resp = self.admin_client.post('/api/v1/admin/users/', {
            'username': 'noemail',
            'password': 'StrongPass99!',
        }, format='json')
        self.assertEqual(resp.status_code, 400)

    def test_create_missing_password_returns_400(self):
        resp = self.admin_client.post('/api/v1/admin/users/', {
            'username': 'nopass',
            'email': 'nopass@test.com',
        }, format='json')
        self.assertEqual(resp.status_code, 400)

    def test_create_audit_log_created(self):
        resp = self.admin_client.post('/api/v1/admin/users/', {
            'username': 'auditcreate',
            'email': 'ac@test.com',
            'password': 'StrongPass99!',
        }, format='json')
        self.assertEqual(resp.status_code, 201)
        user = User.objects.get(username='auditcreate')
        log = UserAuditLog.objects.filter(target_user=user, action='user_created')
        self.assertEqual(log.count(), 1)
        self.assertEqual(log.first().actor, self.admin_user)


class UpdateUserTests(BaseUserManagementTest):
    """Tests for PATCH /api/v1/admin/users/{id}/"""

    def setUp(self):
        super().setUp()
        self.target = self.create_user(
            username='update_target', email='ut@test.com',
        )
        self.target.groups.add(self.support_group)

    def test_update_first_name(self):
        resp = self.admin_client.patch(
            f'/api/v1/admin/users/{self.target.pk}/',
            {'first_name': 'Updated'},
            format='json',
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()['data']['first_name'], 'Updated')

    def test_update_last_name(self):
        resp = self.admin_client.patch(
            f'/api/v1/admin/users/{self.target.pk}/',
            {'last_name': 'NewLast'},
            format='json',
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()['data']['last_name'], 'NewLast')

    def test_update_email_normalized(self):
        resp = self.admin_client.patch(
            f'/api/v1/admin/users/{self.target.pk}/',
            {'email': 'NEW@EMAIL.COM'},
            format='json',
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()['data']['email'], 'new@email.com')

    def test_update_email_duplicate_returns_400(self):
        resp = self.admin_client.patch(
            f'/api/v1/admin/users/{self.target.pk}/',
            {'email': 'ADMIN@TEST.COM'},  # belongs to admin_user
            format='json',
        )
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.json()['code'], 'email_exists')

    def test_update_rejects_username(self):
        resp = self.admin_client.patch(
            f'/api/v1/admin/users/{self.target.pk}/',
            {'username': 'hacker'},
            format='json',
        )
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.json()['code'], 'username_not_editable')

    def test_update_groups_replaces_all(self):
        """Groups field replaces all existing memberships."""
        resp = self.admin_client.patch(
            f'/api/v1/admin/users/{self.target.pk}/',
            {'groups': ['Sales']},
            format='json',
        )
        self.assertEqual(resp.status_code, 200)
        groups = resp.json()['data']['groups']
        self.assertEqual(groups, ['Sales'])
        # Support should be gone
        self.assertNotIn('Support', groups)

    def test_update_groups_empty_removes_all(self):
        resp = self.admin_client.patch(
            f'/api/v1/admin/users/{self.target.pk}/',
            {'groups': []},
            format='json',
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()['data']['groups'], [])

    def test_update_groups_invalid_returns_400(self):
        resp = self.admin_client.patch(
            f'/api/v1/admin/users/{self.target.pk}/',
            {'groups': ['FakeGroup']},
            format='json',
        )
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.json()['code'], 'invalid_groups')

    def test_update_nonexistent_user_returns_404(self):
        resp = self.admin_client.patch(
            '/api/v1/admin/users/99999/',
            {'first_name': 'Ghost'},
            format='json',
        )
        self.assertEqual(resp.status_code, 404)
        self.assertEqual(resp.json()['code'], 'user_not_found')

    def test_update_returns_detail_serializer(self):
        resp = self.admin_client.patch(
            f'/api/v1/admin/users/{self.target.pk}/',
            {'first_name': 'Serializer'},
            format='json',
        )
        data = resp.json()['data']
        self.assertIn('permissions', data)
        self.assertIn('groups', data)
        self.assertNotIn('password', data)

    def test_update_audit_log_created(self):
        resp = self.admin_client.patch(
            f'/api/v1/admin/users/{self.target.pk}/',
            {'first_name': 'Audited'},
            format='json',
        )
        self.assertEqual(resp.status_code, 200)
        log = UserAuditLog.objects.filter(
            target_user=self.target, action='user_updated'
        )
        self.assertEqual(log.count(), 1)
        entry = log.first()
        self.assertEqual(entry.actor, self.admin_user)
        self.assertIn('first_name', entry.metadata.get('old_values', {}))

    def test_update_groups_creates_groups_changed_audit(self):
        resp = self.admin_client.patch(
            f'/api/v1/admin/users/{self.target.pk}/',
            {'groups': ['Admin']},
            format='json',
        )
        self.assertEqual(resp.status_code, 200)
        log = UserAuditLog.objects.filter(
            target_user=self.target, action='groups_changed'
        )
        self.assertEqual(log.count(), 1)

    def test_update_multiple_fields_at_once(self):
        resp = self.admin_client.patch(
            f'/api/v1/admin/users/{self.target.pk}/',
            {'first_name': 'Multi', 'last_name': 'Update', 'is_staff': False},
            format='json',
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()['data']
        self.assertEqual(data['first_name'], 'Multi')
        self.assertEqual(data['last_name'], 'Update')
        self.assertFalse(data['is_staff'])
