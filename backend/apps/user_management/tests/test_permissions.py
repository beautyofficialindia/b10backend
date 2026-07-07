"""
Tests for authentication and authorization on user management endpoints.

Covers:
- 401 Unauthorized for anonymous requests (no JWT token)
- 403 Forbidden for authenticated non-Admin users
- 200/201 for authenticated Admin group members
"""
from django.test import TestCase

from apps.user_management.tests.conftest import BaseUserManagementTest


class AuthenticationTests(BaseUserManagementTest):
    """Test that all endpoints require a valid JWT token (401 without)."""

    def test_list_requires_auth(self):
        resp = self.anon_client.get('/api/v1/admin/users/')
        self.assertEqual(resp.status_code, 401)

    def test_create_requires_auth(self):
        resp = self.anon_client.post('/api/v1/admin/users/', {}, format='json')
        self.assertEqual(resp.status_code, 401)

    def test_retrieve_requires_auth(self):
        resp = self.anon_client.get(f'/api/v1/admin/users/{self.admin_user.pk}/')
        self.assertEqual(resp.status_code, 401)

    def test_update_requires_auth(self):
        resp = self.anon_client.patch(
            f'/api/v1/admin/users/{self.admin_user.pk}/',
            {'first_name': 'Hacker'},
            format='json',
        )
        self.assertEqual(resp.status_code, 401)

    def test_me_requires_auth(self):
        resp = self.anon_client.get('/api/v1/admin/users/me/')
        self.assertEqual(resp.status_code, 401)

    def test_activate_requires_auth(self):
        resp = self.anon_client.post(f'/api/v1/admin/users/{self.inactive_user.pk}/activate/')
        self.assertEqual(resp.status_code, 401)

    def test_deactivate_requires_auth(self):
        resp = self.anon_client.post(f'/api/v1/admin/users/{self.regular_user.pk}/deactivate/')
        self.assertEqual(resp.status_code, 401)

    def test_reset_password_requires_auth(self):
        resp = self.anon_client.post(
            f'/api/v1/admin/users/{self.regular_user.pk}/reset-password/',
            {'password': 'NewPass123!'},
            format='json',
        )
        self.assertEqual(resp.status_code, 401)

    def test_audit_log_requires_auth(self):
        resp = self.anon_client.get(f'/api/v1/admin/users/{self.admin_user.pk}/audit-log/')
        self.assertEqual(resp.status_code, 401)

    def test_bulk_activate_requires_auth(self):
        resp = self.anon_client.post(
            '/api/v1/admin/users/bulk-activate/',
            {'user_ids': [self.inactive_user.pk]},
            format='json',
        )
        self.assertEqual(resp.status_code, 401)

    def test_bulk_deactivate_requires_auth(self):
        resp = self.anon_client.post(
            '/api/v1/admin/users/bulk-deactivate/',
            {'user_ids': [self.regular_user.pk]},
            format='json',
        )
        self.assertEqual(resp.status_code, 401)


class AuthorizationTests(BaseUserManagementTest):
    """Test that non-Admin authenticated users get 403."""

    def test_list_requires_admin_group(self):
        resp = self.regular_client.get('/api/v1/admin/users/')
        self.assertEqual(resp.status_code, 403)

    def test_create_requires_admin_group(self):
        resp = self.regular_client.post(
            '/api/v1/admin/users/',
            {'username': 'hack', 'email': 'h@t.com', 'password': 'P123!'},
            format='json',
        )
        self.assertEqual(resp.status_code, 403)

    def test_retrieve_requires_admin_group(self):
        resp = self.regular_client.get(f'/api/v1/admin/users/{self.admin_user.pk}/')
        self.assertEqual(resp.status_code, 403)

    def test_update_requires_admin_group(self):
        resp = self.regular_client.patch(
            f'/api/v1/admin/users/{self.admin_user.pk}/',
            {'first_name': 'Hack'},
            format='json',
        )
        self.assertEqual(resp.status_code, 403)

    def test_me_requires_admin_group(self):
        resp = self.regular_client.get('/api/v1/admin/users/me/')
        self.assertEqual(resp.status_code, 403)

    def test_activate_requires_admin_group(self):
        resp = self.regular_client.post(f'/api/v1/admin/users/{self.inactive_user.pk}/activate/')
        self.assertEqual(resp.status_code, 403)

    def test_deactivate_requires_admin_group(self):
        resp = self.regular_client.post(f'/api/v1/admin/users/{self.regular_user.pk}/deactivate/')
        self.assertEqual(resp.status_code, 403)

    def test_reset_password_requires_admin_group(self):
        resp = self.regular_client.post(
            f'/api/v1/admin/users/{self.regular_user.pk}/reset-password/',
            {'password': 'NewPass123!'},
            format='json',
        )
        self.assertEqual(resp.status_code, 403)

    def test_audit_log_requires_admin_group(self):
        resp = self.regular_client.get(f'/api/v1/admin/users/{self.admin_user.pk}/audit-log/')
        self.assertEqual(resp.status_code, 403)

    def test_bulk_activate_requires_admin_group(self):
        resp = self.regular_client.post(
            '/api/v1/admin/users/bulk-activate/',
            {'user_ids': [self.inactive_user.pk]},
            format='json',
        )
        self.assertEqual(resp.status_code, 403)

    def test_bulk_deactivate_requires_admin_group(self):
        resp = self.regular_client.post(
            '/api/v1/admin/users/bulk-deactivate/',
            {'user_ids': [self.regular_user.pk]},
            format='json',
        )
        self.assertEqual(resp.status_code, 403)


class AdminAccessTests(BaseUserManagementTest):
    """Test that Admin group members can access all endpoints."""

    def test_list_succeeds_for_admin(self):
        resp = self.admin_client.get('/api/v1/admin/users/')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data['success'])

    def test_create_succeeds_for_admin(self):
        resp = self.admin_client.post('/api/v1/admin/users/', {
            'username': 'newadminuser',
            'email': 'newadmin@test.com',
            'password': 'StrongPass99!',
        }, format='json')
        self.assertEqual(resp.status_code, 201)
        data = resp.json()
        self.assertTrue(data['success'])

    def test_retrieve_succeeds_for_admin(self):
        resp = self.admin_client.get(f'/api/v1/admin/users/{self.regular_user.pk}/')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data['success'])

    def test_update_succeeds_for_admin(self):
        resp = self.admin_client.patch(
            f'/api/v1/admin/users/{self.regular_user.pk}/',
            {'first_name': 'AdminUpdated'},
            format='json',
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['data']['first_name'], 'AdminUpdated')

    def test_me_succeeds_for_admin(self):
        resp = self.admin_client.get('/api/v1/admin/users/me/')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['data']['username'], 'test_admin')

    def test_activate_succeeds_for_admin(self):
        resp = self.admin_client.post(f'/api/v1/admin/users/{self.inactive_user.pk}/activate/')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data['success'])
        self.assertTrue(data['data']['is_active'])

    def test_deactivate_succeeds_for_admin(self):
        resp = self.admin_client.post(f'/api/v1/admin/users/{self.regular_user.pk}/deactivate/')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data['success'])
        self.assertFalse(data['data']['is_active'])

    def test_reset_password_succeeds_for_admin(self):
        resp = self.admin_client.post(
            f'/api/v1/admin/users/{self.regular_user.pk}/reset-password/',
            {'password': 'NewStrongPass99!'},
            format='json',
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data['success'])

    def test_audit_log_succeeds_for_admin(self):
        resp = self.admin_client.get(f'/api/v1/admin/users/{self.admin_user.pk}/audit-log/')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data['success'])

    def test_bulk_activate_succeeds_for_admin(self):
        resp = self.admin_client.post(
            '/api/v1/admin/users/bulk-activate/',
            {'user_ids': [self.inactive_user.pk]},
            format='json',
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data['success'])

    def test_bulk_deactivate_succeeds_for_admin(self):
        target = self.create_user(username='bulk_target', email='bt@test.com')
        resp = self.admin_client.post(
            '/api/v1/admin/users/bulk-deactivate/',
            {'user_ids': [target.pk]},
            format='json',
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data['success'])
