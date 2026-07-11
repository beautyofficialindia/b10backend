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
