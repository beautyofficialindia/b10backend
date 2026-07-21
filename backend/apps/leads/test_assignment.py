from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from apps.leads.models import Lead
from apps.chatbot.models import ConversationSession
import uuid

User = get_user_model()

class LeadAssignmentAPITests(APITestCase):
    def setUp(self):
        # Create users
        self.admin_user = User.objects.create_superuser(
            username='admin', email='admin@example.com', password='password123'
        )
        self.sales_user = User.objects.create_user(
            username='sales', email='sales@example.com', password='password123', is_staff=True
        )
        self.regular_user = User.objects.create_user(
            username='user', email='user@example.com', password='password123'
        )
        
        # Create a Lead
        self.session = ConversationSession.objects.create()
        self.lead = Lead.objects.create(
            conversation=self.session,
            full_name="Test Lead",
            email="lead@example.com",
            requirements="Test requirements"
        )
        self.url = f"/api/v1/admin/leads/{self.lead.id}/assign/"

    def test_assign_lead(self):
        """Test assigning a lead to a valid user."""
        self.client.force_authenticate(user=self.admin_user)
        payload = {"assigned_admin": self.sales_user.id}
        
        response = self.client.patch(self.url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.lead.refresh_from_db()
        self.assertEqual(self.lead.assigned_admin_id, self.sales_user.id)

    def test_reassign_lead(self):
        """Test reassigning an already assigned lead to another user."""
        self.lead.assigned_admin = self.admin_user
        self.lead.save()
        
        self.client.force_authenticate(user=self.admin_user)
        payload = {"assigned_admin": self.sales_user.id}
        
        response = self.client.patch(self.url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.lead.refresh_from_db()
        self.assertEqual(self.lead.assigned_admin_id, self.sales_user.id)

    def test_unassign_lead(self):
        """Test unassigning a lead (setting assigned_admin to null)."""
        self.lead.assigned_admin = self.admin_user
        self.lead.save()
        
        self.client.force_authenticate(user=self.admin_user)
        payload = {"assigned_admin": None}
        
        response = self.client.patch(self.url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.lead.refresh_from_db()
        self.assertIsNone(self.lead.assigned_admin)

    def test_invalid_user_id(self):
        """Test assigning a lead to a non-existent user ID."""
        self.client.force_authenticate(user=self.admin_user)
        payload = {"assigned_admin": 99999}
        
        response = self.client.patch(self.url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        self.lead.refresh_from_db()
        self.assertIsNone(self.lead.assigned_admin)

    def test_unauthorized_access(self):
        """Test that unauthenticated users cannot assign a lead."""
        payload = {"assigned_admin": self.sales_user.id}
        response = self.client.patch(self.url, payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.lead.refresh_from_db()
        self.assertIsNone(self.lead.assigned_admin)

    def test_non_admin_access(self):
        """Test that regular users (non-staff) cannot assign a lead."""
        self.client.force_authenticate(user=self.regular_user)
        payload = {"assigned_admin": self.sales_user.id}
        
        response = self.client.patch(self.url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        self.lead.refresh_from_db()
        self.assertIsNone(self.lead.assigned_admin)

    def test_invalid_lead_id(self):
        """Test assigning a lead that doesn't exist."""
        self.client.force_authenticate(user=self.admin_user)
        invalid_url = f"/api/v1/admin/leads/{uuid.uuid4()}/assign/"
        payload = {"assigned_admin": self.sales_user.id}
        
        response = self.client.patch(invalid_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
