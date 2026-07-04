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
