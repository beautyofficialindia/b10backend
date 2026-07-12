from rest_framework.test import APITestCase
from django.contrib.auth.models import User, Group
from django.urls import reverse

class AuthTests(APITestCase):
    def setUp(self):
        self.group = Group.objects.create(name='Admin')
        self.user = User.objects.create_user(username='testadmin', password='password123')
        self.user.groups.add(self.group)
        self.login_url = reverse('login')

    def test_login(self):
        response = self.client.post(self.login_url, {'username': 'testadmin', 'password': 'password123'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

class ChangePasswordTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='OldPassword123!')
        self.change_password_url = reverse('change_password')

    def test_change_password_success(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.change_password_url, {
            'old_password': 'OldPassword123!',
            'new_password': 'NewPassword123!'
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data['success'])
        
        # Verify old password no longer works
        self.user.refresh_from_db()
        self.assertFalse(self.user.check_password('OldPassword123!'))
        # Verify new password works
        self.assertTrue(self.user.check_password('NewPassword123!'))

    def test_wrong_old_password(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.change_password_url, {
            'old_password': 'WrongPassword123!',
            'new_password': 'NewPassword123!'
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn('old_password', response.data)

    def test_weak_password(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.change_password_url, {
            'old_password': 'OldPassword123!',
            'new_password': '123'
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn('new_password', response.data)

    def test_same_password(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.change_password_url, {
            'old_password': 'OldPassword123!',
            'new_password': 'OldPassword123!'
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn('new_password', response.data)

    def test_unauthenticated(self):
        response = self.client.post(self.change_password_url, {
            'old_password': 'OldPassword123!',
            'new_password': 'NewPassword123!'
        })
        self.assertEqual(response.status_code, 401)

class TestUpdateProfileAPI(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', 
            email='test@example.com',
            first_name='Test',
            last_name='User',
            password='password123'
        )
        self.other_user = User.objects.create_user(
            username='existinguser',
            password='password123'
        )
        self.me_url = reverse('me')

    def test_update_first_name(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(self.me_url, {'first_name': 'Updated'})
        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Updated')

    def test_update_last_name(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(self.me_url, {'last_name': 'Updated'})
        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertEqual(self.user.last_name, 'Updated')

    def test_update_email(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(self.me_url, {'email': 'new@example.com'})
        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, 'new@example.com')

    def test_update_username(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(self.me_url, {'username': 'newuser'})
        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, 'newuser')

    def test_duplicate_username(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(self.me_url, {'username': 'existinguser'})
        self.assertEqual(response.status_code, 400)
        self.assertIn('username', response.data)

    def test_anonymous_request(self):
        response = self.client.patch(self.me_url, {'first_name': 'Hacker'})
        self.assertEqual(response.status_code, 401)

    def test_forbidden_fields_rejected(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(self.me_url, {
            'first_name': 'Hacker',
            'is_superuser': True,
            'is_staff': True
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn('is_superuser', response.data)
        self.assertIn('is_staff', response.data)
        self.assertEqual(response.data['is_superuser'][0], 'This field cannot be updated.')
        
        # Ensure forbidden fields remain unchanged
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_superuser)
        self.assertFalse(self.user.is_staff)
        self.assertEqual(self.user.first_name, 'Test') # Transaction aborted
