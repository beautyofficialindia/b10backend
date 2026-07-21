from rest_framework.test import APITestCase
from rest_framework import status
from apps.leads.models import Lead, LeadAttachment
from unittest.mock import patch
from django.core.files.uploadedfile import SimpleUploadedFile

class PublicContactAPITests(APITestCase):
    def setUp(self):
        self.url = '/api/v1/public/contact/'

    def test_contact_form_submission_success(self):
        payload = {
            "full_name": "John Doe",
            "email": "john.doe@example.com",
            "phone_number": "1234567890",
            "message": "I would like to inquire about your services."
        }
        
        response = self.client.post(self.url, payload, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['success'], True)
        self.assertEqual(
            response.data['message'], 
            "Thank you for contacting B10. Our team will get back to you shortly."
        )

        # Verify Lead was created correctly
        self.assertEqual(Lead.objects.count(), 1)
        lead = Lead.objects.first()
        self.assertEqual(lead.full_name, "John Doe")
        self.assertEqual(lead.email, "john.doe@example.com")
        self.assertEqual(lead.phone, "1234567890")
        self.assertEqual(lead.requirements, "I would like to inquire about your services.")
        self.assertEqual(lead.source, Lead.LeadSourceChoices.WEBSITE_CONTACT_FORM)
        self.assertEqual(lead.status, 'gathering')
        self.assertEqual(lead.lead_score, 0)
        self.assertIsNone(lead.conversation)

    def test_contact_form_validation_errors(self):
        payload = {
            "full_name": "",
            "email": "invalid-email",
            "phone_number": "123",
            "message": "short"
        }
        
        response = self.client.post(self.url, payload, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('full_name', response.data)
        self.assertIn('email', response.data)
        self.assertIn('phone_number', response.data)
        self.assertIn('message', response.data)

        # Verify no Lead was created
        self.assertEqual(Lead.objects.count(), 0)

    def test_missing_fields(self):
        response = self.client.post(self.url, {}, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('full_name', response.data)
        self.assertIn('email', response.data)
        self.assertIn('phone_number', response.data)
        self.assertIn('phone_number', response.data)
        self.assertIn('message', response.data)

    @patch('common.services.cloudinary_service.CloudinaryUploadService.upload_file')
    def test_contact_form_with_attachment_success(self, mock_upload):
        mock_upload.return_value = {
            'secure_url': 'https://res.cloudinary.com/demo/image/upload/v1234567890/test.pdf',
            'public_id': 'test_public_id'
        }
        
        # Create a mock PDF file with correct magic numbers for PDF (%PDF-)
        file_content = b'%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n>>\nendobj\n'
        mock_file = SimpleUploadedFile("test.pdf", file_content, content_type="application/pdf")
        
        payload = {
            "full_name": "Jane Doe",
            "email": "jane.doe@example.com",
            "phone_number": "0987654321",
            "message": "I have attached my requirements.",
            "attachment": mock_file
        }
        
        response = self.client.post(self.url, payload, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Lead.objects.count(), 1)
        self.assertEqual(LeadAttachment.objects.count(), 1)
        
        attachment = LeadAttachment.objects.first()
        self.assertEqual(attachment.file_name, "test.pdf")
        self.assertEqual(attachment.file_url, 'https://res.cloudinary.com/demo/image/upload/v1234567890/test.pdf')
        self.assertFalse(attachment.is_public)

    @patch('common.services.cloudinary_service.CloudinaryUploadService.upload_file')
    def test_contact_form_upload_failure_rolls_back(self, mock_upload):
        mock_upload.side_effect = Exception("Cloudinary API Error")
        
        file_content = b'%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n>>\nendobj\n'
        mock_file = SimpleUploadedFile("test.pdf", file_content, content_type="application/pdf")
        
        payload = {
            "full_name": "Fail Doe",
            "email": "fail@example.com",
            "phone_number": "0987654321",
            "message": "This should fail.",
            "attachment": mock_file
        }
        
        response = self.client.post(self.url, payload, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertFalse(response.data['success'])
        
        # Verify atomic transaction rolled back
        self.assertEqual(Lead.objects.count(), 0)
        self.assertEqual(LeadAttachment.objects.count(), 0)

