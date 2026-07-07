"""
Tests for GET /api/v1/admin/users/ — list endpoint.

Covers:
- Pagination (default, custom page_size, empty page, out-of-range)
- Search (username, email, first_name, last_name, partial, case-insensitive)
- Filtering (is_active, is_staff, is_superuser, group, date ranges)
- Ordering (username, email, date_joined, last_login, asc, desc)
- Response structure (pagination meta, serialized fields, groups list)
"""
from datetime import timedelta

from django.utils import timezone

from apps.user_management.tests.conftest import BaseUserManagementTest


class PaginationTests(BaseUserManagementTest):
    """Tests for pagination behavior."""

    def test_default_page_size_is_20(self):
        """Default page returns up to 20 results with pagination meta."""
        resp = self.admin_client.get('/api/v1/admin/users/')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        meta = data['meta']['pagination']
        self.assertEqual(meta['page'], 1)
        self.assertEqual(meta['page_size'], 20)
        self.assertIn('total_count', meta)
        self.assertIn('total_pages', meta)

    def test_custom_page_size(self):
        """page_size query param limits results."""
        resp = self.admin_client.get('/api/v1/admin/users/?page_size=2')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        meta = data['meta']['pagination']
        self.assertEqual(meta['page_size'], 2)
        self.assertLessEqual(len(data['data']), 2)

    def test_page_2(self):
        """Can request page 2."""
        # Create enough users to have page 2 with page_size=1
        resp = self.admin_client.get('/api/v1/admin/users/?page_size=1&page=2')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        meta = data['meta']['pagination']
        self.assertEqual(meta['page'], 2)

    def test_out_of_range_page_returns_404(self):
        """Requesting a page beyond total_pages returns 404."""
        resp = self.admin_client.get('/api/v1/admin/users/?page=9999')
        self.assertEqual(resp.status_code, 404)

    def test_empty_result_set(self):
        """A filter that matches no users returns empty data with pagination meta."""
        resp = self.admin_client.get('/api/v1/admin/users/?search=zzzznonexistent')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data['data'], [])
        meta = data['meta']['pagination']
        self.assertEqual(meta['total_count'], 0)

    def test_max_page_size_capped_at_100(self):
        """page_size larger than 100 is capped."""
        resp = self.admin_client.get('/api/v1/admin/users/?page_size=200')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        meta = data['meta']['pagination']
        self.assertLessEqual(meta['page_size'], 100)


class SearchTests(BaseUserManagementTest):
    """Tests for search functionality (OR across 4 fields, case-insensitive, partial)."""

    def setUp(self):
        super().setUp()
        self.search_user = self.create_user(
            username='findme_john',
            email='unique_search@domain.com',
            first_name='Bartholomew',
            last_name='Zephyrson',
        )

    def test_search_by_username(self):
        resp = self.admin_client.get('/api/v1/admin/users/?search=findme')
        data = resp.json()
        usernames = [u['username'] for u in data['data']]
        self.assertIn('findme_john', usernames)

    def test_search_by_email(self):
        resp = self.admin_client.get('/api/v1/admin/users/?search=unique_search')
        data = resp.json()
        usernames = [u['username'] for u in data['data']]
        self.assertIn('findme_john', usernames)

    def test_search_by_first_name(self):
        resp = self.admin_client.get('/api/v1/admin/users/?search=bartholomew')
        data = resp.json()
        usernames = [u['username'] for u in data['data']]
        self.assertIn('findme_john', usernames)

    def test_search_by_last_name(self):
        resp = self.admin_client.get('/api/v1/admin/users/?search=zephyr')
        data = resp.json()
        usernames = [u['username'] for u in data['data']]
        self.assertIn('findme_john', usernames)

    def test_search_is_case_insensitive(self):
        resp = self.admin_client.get('/api/v1/admin/users/?search=FINDME')
        data = resp.json()
        usernames = [u['username'] for u in data['data']]
        self.assertIn('findme_john', usernames)

    def test_search_partial_match(self):
        """Partial substring matches work."""
        resp = self.admin_client.get('/api/v1/admin/users/?search=artho')
        data = resp.json()
        usernames = [u['username'] for u in data['data']]
        self.assertIn('findme_john', usernames)

    def test_search_no_match(self):
        """Search term that matches nothing returns empty results."""
        resp = self.admin_client.get('/api/v1/admin/users/?search=xyznonexistent123')
        data = resp.json()
        self.assertEqual(len(data['data']), 0)


class FilterTests(BaseUserManagementTest):
    """Tests for boolean, group, and date range filters."""

    def setUp(self):
        super().setUp()
        self.staff_user = self.create_user(
            username='staff_only', email='staff@test.com',
            is_staff=True, is_active=True,
        )
        self.non_staff_user = self.create_user(
            username='non_staff', email='nonstaff@test.com',
            is_staff=False, is_active=True,
        )

    def test_filter_is_active_true(self):
        resp = self.admin_client.get('/api/v1/admin/users/?is_active=true')
        data = resp.json()
        for user in data['data']:
            self.assertTrue(user['is_active'])

    def test_filter_is_active_false(self):
        resp = self.admin_client.get('/api/v1/admin/users/?is_active=false')
        data = resp.json()
        for user in data['data']:
            self.assertFalse(user['is_active'])
        # Should include inactive_user
        usernames = [u['username'] for u in data['data']]
        self.assertIn('test_inactive', usernames)

    def test_filter_is_staff_true(self):
        resp = self.admin_client.get('/api/v1/admin/users/?is_staff=true')
        data = resp.json()
        for user in data['data']:
            self.assertTrue(user['is_staff'])

    def test_filter_is_staff_false(self):
        resp = self.admin_client.get('/api/v1/admin/users/?is_staff=false')
        data = resp.json()
        for user in data['data']:
            self.assertFalse(user['is_staff'])

    def test_filter_is_superuser_true(self):
        resp = self.admin_client.get('/api/v1/admin/users/?is_superuser=true')
        data = resp.json()
        for user in data['data']:
            self.assertTrue(user['is_superuser'])
        usernames = [u['username'] for u in data['data']]
        self.assertIn('test_admin', usernames)

    def test_filter_is_superuser_false(self):
        resp = self.admin_client.get('/api/v1/admin/users/?is_superuser=false')
        data = resp.json()
        for user in data['data']:
            self.assertFalse(user['is_superuser'])

    def test_filter_by_group(self):
        resp = self.admin_client.get('/api/v1/admin/users/?group=Support')
        data = resp.json()
        for user in data['data']:
            self.assertIn('Support', user['groups'])
        usernames = [u['username'] for u in data['data']]
        self.assertIn('test_regular', usernames)

    def test_filter_by_group_no_match(self):
        resp = self.admin_client.get('/api/v1/admin/users/?group=NonExistentGroup')
        data = resp.json()
        self.assertEqual(len(data['data']), 0)

    def test_filter_date_joined_after(self):
        yesterday = (timezone.now() - timedelta(days=1)).strftime('%Y-%m-%dT%H:%M:%SZ')
        resp = self.admin_client.get(f'/api/v1/admin/users/?date_joined_after={yesterday}')
        data = resp.json()
        # All fixture users were created "now" so should all appear
        self.assertGreater(len(data['data']), 0)

    def test_filter_date_joined_before(self):
        tomorrow = (timezone.now() + timedelta(days=1)).strftime('%Y-%m-%dT%H:%M:%SZ')
        resp = self.admin_client.get(f'/api/v1/admin/users/?date_joined_before={tomorrow}')
        data = resp.json()
        self.assertGreater(len(data['data']), 0)

    def test_filter_date_joined_range_excludes(self):
        """A range in the past should exclude all recently-created users."""
        old_date = (timezone.now() - timedelta(days=365)).strftime('%Y-%m-%dT%H:%M:%SZ')
        older_date = (timezone.now() - timedelta(days=366)).strftime('%Y-%m-%dT%H:%M:%SZ')
        resp = self.admin_client.get(
            f'/api/v1/admin/users/?date_joined_after={older_date}&date_joined_before={old_date}'
        )
        data = resp.json()
        self.assertEqual(len(data['data']), 0)

    def test_filter_last_login_after(self):
        """Users who logged in recently."""
        # Explicitly set last_login for admin_user
        from django.contrib.auth import get_user_model
        User = get_user_model()
        User.objects.filter(pk=self.admin_user.pk).update(last_login=timezone.now())

        yesterday = (timezone.now() - timedelta(days=1)).strftime('%Y-%m-%dT%H:%M:%SZ')
        resp = self.admin_client.get(f'/api/v1/admin/users/?last_login_after={yesterday}')
        data = resp.json()
        usernames = [u['username'] for u in data['data']]
        self.assertIn('test_admin', usernames)

    def test_filter_last_login_before(self):
        """Filter last_login_before in the far future returns all who have logged in."""
        # Explicitly set last_login for admin_user
        from django.contrib.auth import get_user_model
        User = get_user_model()
        User.objects.filter(pk=self.admin_user.pk).update(last_login=timezone.now())

        future = (timezone.now() + timedelta(days=1)).strftime('%Y-%m-%dT%H:%M:%SZ')
        resp = self.admin_client.get(f'/api/v1/admin/users/?last_login_before={future}')
        data = resp.json()
        self.assertGreater(len(data['data']), 0)


class OrderingTests(BaseUserManagementTest):
    """Tests for ordering results."""

    def setUp(self):
        super().setUp()
        self.user_a = self.create_user(username='aaa_first', email='aaa@test.com')
        self.user_z = self.create_user(username='zzz_last', email='zzz@test.com')

    def test_ordering_username_asc(self):
        resp = self.admin_client.get('/api/v1/admin/users/?ordering=username')
        data = resp.json()
        usernames = [u['username'] for u in data['data']]
        self.assertEqual(usernames, sorted(usernames))

    def test_ordering_username_desc(self):
        resp = self.admin_client.get('/api/v1/admin/users/?ordering=-username')
        data = resp.json()
        usernames = [u['username'] for u in data['data']]
        self.assertEqual(usernames, sorted(usernames, reverse=True))

    def test_ordering_email_asc(self):
        resp = self.admin_client.get('/api/v1/admin/users/?ordering=email')
        data = resp.json()
        emails = [u['email'] for u in data['data']]
        self.assertEqual(emails, sorted(emails))

    def test_ordering_email_desc(self):
        resp = self.admin_client.get('/api/v1/admin/users/?ordering=-email')
        data = resp.json()
        emails = [u['email'] for u in data['data']]
        self.assertEqual(emails, sorted(emails, reverse=True))

    def test_ordering_date_joined_asc(self):
        resp = self.admin_client.get('/api/v1/admin/users/?ordering=date_joined')
        data = resp.json()
        dates = [u['date_joined'] for u in data['data']]
        self.assertEqual(dates, sorted(dates))

    def test_ordering_date_joined_desc(self):
        resp = self.admin_client.get('/api/v1/admin/users/?ordering=-date_joined')
        data = resp.json()
        dates = [u['date_joined'] for u in data['data']]
        self.assertEqual(dates, sorted(dates, reverse=True))

    def test_ordering_first_name_asc(self):
        resp = self.admin_client.get('/api/v1/admin/users/?ordering=first_name')
        data = resp.json()
        names = [u['first_name'] for u in data['data']]
        self.assertEqual(names, sorted(names))

    def test_ordering_last_name_asc(self):
        resp = self.admin_client.get('/api/v1/admin/users/?ordering=last_name')
        data = resp.json()
        names = [u['last_name'] for u in data['data']]
        self.assertEqual(names, sorted(names))

    def test_ordering_invalid_field_uses_default(self):
        """An invalid ordering field falls back to -date_joined."""
        resp = self.admin_client.get('/api/v1/admin/users/?ordering=invalid_field')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        dates = [u['date_joined'] for u in data['data']]
        self.assertEqual(dates, sorted(dates, reverse=True))


class ResponseStructureTests(BaseUserManagementTest):
    """Tests for response format and field presence."""

    def test_list_response_envelope(self):
        """List response has success, data, message, meta keys."""
        resp = self.admin_client.get('/api/v1/admin/users/')
        data = resp.json()
        self.assertIn('success', data)
        self.assertIn('data', data)
        self.assertIn('meta', data)
        self.assertTrue(data['success'])

    def test_list_pagination_meta_structure(self):
        """Pagination meta contains page, page_size, total_count, total_pages."""
        resp = self.admin_client.get('/api/v1/admin/users/')
        meta = resp.json()['meta']['pagination']
        self.assertIn('page', meta)
        self.assertIn('page_size', meta)
        self.assertIn('total_count', meta)
        self.assertIn('total_pages', meta)

    def test_list_serializer_fields(self):
        """Each user in list has exactly the List_Serializer fields."""
        resp = self.admin_client.get('/api/v1/admin/users/')
        data = resp.json()
        expected_fields = {
            'id', 'username', 'email', 'first_name', 'last_name',
            'is_active', 'is_staff', 'is_superuser', 'groups',
            'date_joined', 'last_login',
        }
        for user in data['data']:
            self.assertEqual(set(user.keys()), expected_fields)

    def test_list_does_not_include_password(self):
        """No password field in list results."""
        resp = self.admin_client.get('/api/v1/admin/users/')
        for user in resp.json()['data']:
            self.assertNotIn('password', user)

    def test_list_does_not_include_permissions(self):
        """List serializer does NOT include permissions (that's detail only)."""
        resp = self.admin_client.get('/api/v1/admin/users/')
        for user in resp.json()['data']:
            self.assertNotIn('permissions', user)

    def test_groups_field_is_list_of_strings(self):
        """Groups field is a list of group name strings."""
        resp = self.admin_client.get('/api/v1/admin/users/')
        data = resp.json()
        admin_data = next(u for u in data['data'] if u['username'] == 'test_admin')
        self.assertIsInstance(admin_data['groups'], list)
        self.assertIn('Admin', admin_data['groups'])
        # Each group is a string
        for g in admin_data['groups']:
            self.assertIsInstance(g, str)

    def test_total_count_matches_actual_users(self):
        """total_count in pagination meta matches actual user count."""
        from django.contrib.auth import get_user_model
        User = get_user_model()
        resp = self.admin_client.get('/api/v1/admin/users/')
        meta = resp.json()['meta']['pagination']
        self.assertEqual(meta['total_count'], User.objects.count())
