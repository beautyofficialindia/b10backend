"""Comprehensive tests for the Roles Management module."""
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission

from apps.role_management.tests.conftest import BaseRoleManagementTest
from apps.user_management.models import UserAuditLog

User = get_user_model()


# ═══════════════════════════════════════════════════════════════════
# 1. Authentication & Authorization
# ═══════════════════════════════════════════════════════════════════

class AuthTests(BaseRoleManagementTest):
    def test_anon_list_401(self):
        self.assertEqual(self.anon_client.get('/api/v1/admin/roles/').status_code, 401)

    def test_anon_create_401(self):
        self.assertEqual(self.anon_client.post('/api/v1/admin/roles/', {}, format='json').status_code, 401)

    def test_nonadmin_list_403(self):
        self.assertEqual(self.regular_client.get('/api/v1/admin/roles/').status_code, 403)

    def test_nonadmin_create_403(self):
        self.assertEqual(self.regular_client.post('/api/v1/admin/roles/', {'name': 'X'}, format='json').status_code, 403)

    def test_admin_list_200(self):
        self.assertEqual(self.admin_client.get('/api/v1/admin/roles/').status_code, 200)


# ═══════════════════════════════════════════════════════════════════
# 2. Role CRUD
# ═══════════════════════════════════════════════════════════════════

class RoleCRUDTests(BaseRoleManagementTest):
    def test_list_roles(self):
        resp = self.admin_client.get('/api/v1/admin/roles/')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data['success'])
        self.assertGreaterEqual(len(data['data']), 3)

    def test_list_has_counts(self):
        resp = self.admin_client.get('/api/v1/admin/roles/')
        for role in resp.json()['data']:
            self.assertIn('permissions_count', role)
            self.assertIn('users_count', role)

    def test_create_role(self):
        resp = self.admin_client.post('/api/v1/admin/roles/', {'name': 'NewRole'}, format='json')
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(resp.json()['data']['name'], 'NewRole')

    def test_create_with_permissions(self):
        codename = self.get_permission_codename()
        resp = self.admin_client.post('/api/v1/admin/roles/', {
            'name': 'WithPerms', 'permissions': [codename],
        }, format='json')
        self.assertEqual(resp.status_code, 201)
        self.assertGreater(len(resp.json()['data']['permissions']), 0)

    def test_create_duplicate_name_400(self):
        self.admin_client.post('/api/v1/admin/roles/', {'name': 'Dup'}, format='json')
        resp = self.admin_client.post('/api/v1/admin/roles/', {'name': 'DUP'}, format='json')
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.json()['code'], 'role_name_exists')

    def test_create_invalid_permission_400(self):
        resp = self.admin_client.post('/api/v1/admin/roles/', {
            'name': 'BadPerm', 'permissions': ['fake.perm'],
        }, format='json')
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.json()['code'], 'invalid_permissions')

    def test_create_missing_name_400(self):
        resp = self.admin_client.post('/api/v1/admin/roles/', {}, format='json')
        self.assertEqual(resp.status_code, 400)

    def test_retrieve_role(self):
        resp = self.admin_client.get(f'/api/v1/admin/roles/{self.admin_group.pk}/')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()['data']
        self.assertEqual(data['name'], 'Admin')
        self.assertIn('permissions', data)
        self.assertIn('users_count', data)

    def test_retrieve_404(self):
        resp = self.admin_client.get('/api/v1/admin/roles/99999/')
        self.assertEqual(resp.status_code, 404)

    def test_update_role(self):
        role = Group.objects.create(name='ToUpdate')
        resp = self.admin_client.patch(f'/api/v1/admin/roles/{role.pk}/', {'name': 'Updated'}, format='json')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()['data']['name'], 'Updated')

    def test_update_duplicate_name_400(self):
        role = Group.objects.create(name='UniqueRole')
        resp = self.admin_client.patch(f'/api/v1/admin/roles/{role.pk}/', {'name': 'Admin'}, format='json')
        self.assertEqual(resp.status_code, 400)

    def test_update_404(self):
        resp = self.admin_client.patch('/api/v1/admin/roles/99999/', {'name': 'X'}, format='json')
        self.assertEqual(resp.status_code, 404)

    def test_delete_role(self):
        role = Group.objects.create(name='ToDelete')
        resp = self.admin_client.delete(f'/api/v1/admin/roles/{role.pk}/')
        self.assertEqual(resp.status_code, 204)
        self.assertFalse(Group.objects.filter(pk=role.pk).exists())

    def test_delete_404(self):
        resp = self.admin_client.delete('/api/v1/admin/roles/99999/')
        self.assertEqual(resp.status_code, 404)


# ═══════════════════════════════════════════════════════════════════
# 3. Protected Roles
# ═══════════════════════════════════════════════════════════════════

class ProtectedRoleTests(BaseRoleManagementTest):
    def test_cannot_delete_admin(self):
        resp = self.admin_client.delete(f'/api/v1/admin/roles/{self.admin_group.pk}/')
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.json()['code'], 'role_protected')

    def test_cannot_delete_sales(self):
        resp = self.admin_client.delete(f'/api/v1/admin/roles/{self.sales_group.pk}/')
        self.assertEqual(resp.status_code, 400)

    def test_cannot_delete_support(self):
        resp = self.admin_client.delete(f'/api/v1/admin/roles/{self.support_group.pk}/')
        self.assertEqual(resp.status_code, 400)


# ═══════════════════════════════════════════════════════════════════
# 4. Permission Management
# ═══════════════════════════════════════════════════════════════════

class PermissionManagementTests(BaseRoleManagementTest):
    def setUp(self):
        super().setUp()
        self.role = Group.objects.create(name='PermRole')
        self.codename = self.get_permission_codename()

    def test_set_permissions(self):
        resp = self.admin_client.put(
            f'/api/v1/admin/roles/{self.role.pk}/set-permissions/',
            {'permissions': [self.codename]}, format='json',
        )
        self.assertEqual(resp.status_code, 200)
        self.assertGreater(len(resp.json()['data']['permissions']), 0)

    def test_set_permissions_empty_clears(self):
        self.role.permissions.add(Permission.objects.first())
        resp = self.admin_client.put(
            f'/api/v1/admin/roles/{self.role.pk}/set-permissions/',
            {'permissions': []}, format='json',
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.json()['data']['permissions']), 0)

    def test_set_permissions_invalid_400(self):
        resp = self.admin_client.put(
            f'/api/v1/admin/roles/{self.role.pk}/set-permissions/',
            {'permissions': ['fake.perm']}, format='json',
        )
        self.assertEqual(resp.status_code, 400)

    def test_assign_permissions(self):
        resp = self.admin_client.post(
            f'/api/v1/admin/roles/{self.role.pk}/assign-permissions/',
            {'permissions': [self.codename]}, format='json',
        )
        self.assertEqual(resp.status_code, 200)

    def test_remove_permissions(self):
        perm = Permission.objects.first()
        self.role.permissions.add(perm)
        resp = self.admin_client.post(
            f'/api/v1/admin/roles/{self.role.pk}/remove-permissions/',
            {'permissions': [self.codename]}, format='json',
        )
        self.assertEqual(resp.status_code, 200)

    def test_get_role_permissions(self):
        resp = self.admin_client.get(f'/api/v1/admin/roles/{self.role.pk}/permissions/')
        self.assertEqual(resp.status_code, 200)

    def test_list_available_permissions(self):
        resp = self.admin_client.get('/api/v1/admin/roles/permissions/')
        self.assertEqual(resp.status_code, 200)
        self.assertGreater(len(resp.json()['data']), 0)

    def test_permissions_404(self):
        resp = self.admin_client.put(
            '/api/v1/admin/roles/99999/set-permissions/',
            {'permissions': []}, format='json',
        )
        self.assertEqual(resp.status_code, 404)


# ═══════════════════════════════════════════════════════════════════
# 5. User Membership
# ═══════════════════════════════════════════════════════════════════

class UserMembershipTests(BaseRoleManagementTest):
    def setUp(self):
        super().setUp()
        self.role = Group.objects.create(name='MemberRole')
        self.target = User.objects.create_user(
            username='member_target', email='mt@test.com', password='Pass123!',
        )

    def test_add_users(self):
        resp = self.admin_client.post(
            f'/api/v1/admin/roles/{self.role.pk}/assign-users/',
            {'user_ids': [self.target.pk]}, format='json',
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()['data']['added_count'], 1)
        self.assertTrue(self.role.user_set.filter(pk=self.target.pk).exists())

    def test_add_users_already_in_role(self):
        self.role.user_set.add(self.target)
        resp = self.admin_client.post(
            f'/api/v1/admin/roles/{self.role.pk}/assign-users/',
            {'user_ids': [self.target.pk]}, format='json',
        )
        self.assertEqual(resp.json()['data']['added_count'], 0)
        self.assertEqual(resp.json()['data']['skipped'][0]['reason'], 'already in role')

    def test_add_users_not_found(self):
        resp = self.admin_client.post(
            f'/api/v1/admin/roles/{self.role.pk}/assign-users/',
            {'user_ids': [99999]}, format='json',
        )
        self.assertEqual(resp.json()['data']['skipped'][0]['reason'], 'user not found')

    def test_remove_users(self):
        self.role.user_set.add(self.target)
        resp = self.admin_client.post(
            f'/api/v1/admin/roles/{self.role.pk}/remove-users/',
            {'user_ids': [self.target.pk]}, format='json',
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()['data']['removed_count'], 1)
        self.assertFalse(self.role.user_set.filter(pk=self.target.pk).exists())

    def test_remove_users_not_in_role(self):
        resp = self.admin_client.post(
            f'/api/v1/admin/roles/{self.role.pk}/remove-users/',
            {'user_ids': [self.target.pk]}, format='json',
        )
        self.assertEqual(resp.json()['data']['skipped'][0]['reason'], 'not in role')

    def test_remove_last_superuser_from_admin_blocked(self):
        """Cannot remove last active superuser from Admin role."""
        resp = self.admin_client.post(
            f'/api/v1/admin/roles/{self.admin_group.pk}/remove-users/',
            {'user_ids': [self.admin_user.pk]}, format='json',
        )
        data = resp.json()['data']
        self.assertEqual(data['removed_count'], 0)
        self.assertIn('cannot remove last active superuser', data['skipped'][0]['reason'])

    def test_list_role_users(self):
        self.role.user_set.add(self.target)
        resp = self.admin_client.get(f'/api/v1/admin/roles/{self.role.pk}/users/')
        self.assertEqual(resp.status_code, 200)
        usernames = [u['username'] for u in resp.json()['data']]
        self.assertIn('member_target', usernames)

    def test_list_role_users_search(self):
        self.role.user_set.add(self.target)
        resp = self.admin_client.get(f'/api/v1/admin/roles/{self.role.pk}/users/?search=member')
        self.assertEqual(len(resp.json()['data']), 1)

    def test_list_role_users_empty(self):
        resp = self.admin_client.get(f'/api/v1/admin/roles/{self.role.pk}/users/')
        self.assertEqual(len(resp.json()['data']), 0)

    def test_role_users_404(self):
        resp = self.admin_client.get('/api/v1/admin/roles/99999/users/')
        self.assertEqual(resp.status_code, 404)


# ═══════════════════════════════════════════════════════════════════
# 6. Search / Ordering / Pagination
# ═══════════════════════════════════════════════════════════════════

class SearchOrderingPaginationTests(BaseRoleManagementTest):
    def test_search_by_name(self):
        Group.objects.create(name='Searchable')
        resp = self.admin_client.get('/api/v1/admin/roles/?search=Searchable')
        names = [r['name'] for r in resp.json()['data']]
        self.assertIn('Searchable', names)

    def test_search_case_insensitive(self):
        Group.objects.create(name='CaseTest')
        resp = self.admin_client.get('/api/v1/admin/roles/?search=casetest')
        names = [r['name'] for r in resp.json()['data']]
        self.assertIn('CaseTest', names)

    def test_ordering_name_asc(self):
        resp = self.admin_client.get('/api/v1/admin/roles/?ordering=name')
        names = [r['name'] for r in resp.json()['data']]
        self.assertEqual(names, sorted(names))

    def test_ordering_name_desc(self):
        resp = self.admin_client.get('/api/v1/admin/roles/?ordering=-name')
        names = [r['name'] for r in resp.json()['data']]
        self.assertEqual(names, sorted(names, reverse=True))

    def test_pagination(self):
        resp = self.admin_client.get('/api/v1/admin/roles/?page_size=1')
        meta = resp.json()['meta']['pagination']
        self.assertEqual(meta['page_size'], 1)
        self.assertEqual(len(resp.json()['data']), 1)
        self.assertGreater(meta['total_count'], 1)

    def test_search_no_results(self):
        resp = self.admin_client.get('/api/v1/admin/roles/?search=zzzznonexistent')
        self.assertEqual(len(resp.json()['data']), 0)


# ═══════════════════════════════════════════════════════════════════
# 7. Audit Logging
# ═══════════════════════════════════════════════════════════════════

class AuditLogTests(BaseRoleManagementTest):
    def test_create_logs_audit(self):
        self.admin_client.post('/api/v1/admin/roles/', {'name': 'AuditCreate'}, format='json')
        self.assertTrue(UserAuditLog.objects.filter(action='role_created').exists())

    def test_update_logs_audit(self):
        role = Group.objects.create(name='AuditUpdate')
        self.admin_client.patch(f'/api/v1/admin/roles/{role.pk}/', {'name': 'AuditUpdated'}, format='json')
        self.assertTrue(UserAuditLog.objects.filter(action='role_updated').exists())

    def test_delete_logs_audit(self):
        role = Group.objects.create(name='AuditDelete')
        self.admin_client.delete(f'/api/v1/admin/roles/{role.pk}/')
        self.assertTrue(UserAuditLog.objects.filter(action='role_deleted').exists())

    def test_set_permissions_logs_audit(self):
        role = Group.objects.create(name='AuditPerms')
        self.admin_client.put(
            f'/api/v1/admin/roles/{role.pk}/set-permissions/',
            {'permissions': []}, format='json',
        )
        self.assertTrue(UserAuditLog.objects.filter(action='role_permissions_changed').exists())

    def test_assign_permissions_logs_audit(self):
        role = Group.objects.create(name='AuditAssignPerm')
        codename = self.get_permission_codename()
        self.admin_client.post(
            f'/api/v1/admin/roles/{role.pk}/assign-permissions/',
            {'permissions': [codename]}, format='json',
        )
        self.assertEqual(UserAuditLog.objects.filter(action='role_permissions_changed').count(), 1)

    def test_remove_permissions_logs_audit(self):
        role = Group.objects.create(name='AuditRemovePerm')
        perm = Permission.objects.first()
        role.permissions.add(perm)
        codename = f"{perm.content_type.app_label}.{perm.codename}"
        self.admin_client.post(
            f'/api/v1/admin/roles/{role.pk}/remove-permissions/',
            {'permissions': [codename]}, format='json',
        )
        self.assertEqual(UserAuditLog.objects.filter(action='role_permissions_changed').count(), 1)

    def test_add_users_logs_audit(self):
        role = Group.objects.create(name='AuditAddUser')
        self.admin_client.post(
            f'/api/v1/admin/roles/{role.pk}/assign-users/',
            {'user_ids': [self.regular_user.pk]}, format='json',
        )
        self.assertTrue(UserAuditLog.objects.filter(action='role_users_added').exists())

    def test_remove_users_logs_audit(self):
        role = Group.objects.create(name='AuditRemoveUser')
        role.user_set.add(self.regular_user)
        self.admin_client.post(
            f'/api/v1/admin/roles/{role.pk}/remove-users/',
            {'user_ids': [self.regular_user.pk]}, format='json',
        )
        self.assertTrue(UserAuditLog.objects.filter(action='role_users_removed').exists())

    def test_failed_create_no_audit(self):
        initial = UserAuditLog.objects.count()
        self.admin_client.post('/api/v1/admin/roles/', {'name': 'Admin'}, format='json')
        self.assertEqual(UserAuditLog.objects.count(), initial)

    def test_failed_delete_no_audit(self):
        initial = UserAuditLog.objects.count()
        self.admin_client.delete(f'/api/v1/admin/roles/{self.admin_group.pk}/')
        self.assertEqual(UserAuditLog.objects.count(), initial)

    def test_audit_has_actor(self):
        self.admin_client.post('/api/v1/admin/roles/', {'name': 'ActorCheck'}, format='json')
        log = UserAuditLog.objects.get(action='role_created')
        self.assertEqual(log.actor, self.admin_user)

    def test_audit_has_metadata(self):
        self.admin_client.post('/api/v1/admin/roles/', {'name': 'MetaCheck'}, format='json')
        log = UserAuditLog.objects.get(action='role_created')
        self.assertIn('role_name', log.metadata)
