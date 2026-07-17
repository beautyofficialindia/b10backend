from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.utils import timezone
from datetime import timedelta
from rest_framework.test import APIClient
from rest_framework import status as http_status

from .models import Notification
from .services import NotificationService, MAX_NOTIFICATIONS

User = get_user_model()


# =============================================================================
# Model Tests
# =============================================================================

class NotificationModelTests(TestCase):

    def test_create_notification_defaults(self):
        n = Notification.objects.create(
            title='Test Notification',
            message='Test message',
            type=Notification.Type.INFO,
            category=Notification.Category.SYSTEM,
        )
        self.assertFalse(n.is_read)
        self.assertIsNone(n.actor)
        self.assertIsNone(n.recipient)
        self.assertEqual(n.action_url, '')

    def test_str_representation(self):
        n = Notification.objects.create(
            title='Lead Converted',
            message='',
            type=Notification.Type.SUCCESS,
            category=Notification.Category.LEADS,
        )
        self.assertEqual(str(n), '[SUCCESS] Lead Converted')

    def test_default_ordering_newest_first(self):
        n1 = Notification.objects.create(title='First', message='', type='INFO', category='SYSTEM')
        n2 = Notification.objects.create(title='Second', message='', type='INFO', category='SYSTEM')
        results = list(Notification.objects.all())
        self.assertEqual(results[0].id, n2.id)
        self.assertEqual(results[1].id, n1.id)


# =============================================================================
# Service Tests
# =============================================================================

class NotificationServiceTests(TestCase):

    def test_create(self):
        n = NotificationService.create(
            title='System Alert',
            message='Something happened.',
            type=Notification.Type.INFO,
            category=Notification.Category.SYSTEM,
        )
        self.assertIsNotNone(n.id)
        self.assertEqual(n.title, 'System Alert')
        self.assertFalse(n.is_read)

    def test_create_with_actor(self):
        user = User.objects.create_user(username='actor', password='pass')
        n = NotificationService.create_success(
            title='Lead Converted',
            message='Done.',
            category=Notification.Category.LEADS,
            actor=user,
        )
        self.assertEqual(n.actor, user)
        self.assertEqual(n.type, Notification.Type.SUCCESS)

    def test_create_info_helper(self):
        n = NotificationService.create_info('Info', 'msg', Notification.Category.ANALYTICS)
        self.assertEqual(n.type, Notification.Type.INFO)

    def test_create_success_helper(self):
        n = NotificationService.create_success('Win', 'msg', Notification.Category.CRM)
        self.assertEqual(n.type, Notification.Type.SUCCESS)

    def test_create_notice_helper(self):
        n = NotificationService.create_notice('Cache Cleared', 'msg', Notification.Category.SYSTEM)
        self.assertEqual(n.type, Notification.Type.NOTICE)

    def test_create_warning_helper(self):
        n = NotificationService.create_warning('High Load', 'msg', Notification.Category.SYSTEM)
        self.assertEqual(n.type, Notification.Type.WARNING)

    def test_create_critical_helper(self):
        n = NotificationService.create_critical('Breach', 'msg', Notification.Category.SECURITY)
        self.assertEqual(n.type, Notification.Type.CRITICAL)

    def test_mark_read(self):
        n = NotificationService.create('T', 'M', 'INFO', 'SYSTEM')
        self.assertFalse(n.is_read)
        updated = NotificationService.mark_read(n.id)
        self.assertTrue(updated.is_read)
        # Verify persisted
        self.assertTrue(Notification.objects.get(id=n.id).is_read)

    def test_mark_unread(self):
        n = NotificationService.create('T', 'M', 'INFO', 'SYSTEM')
        NotificationService.mark_read(n.id)
        updated = NotificationService.mark_unread(n.id)
        self.assertFalse(updated.is_read)
        self.assertFalse(Notification.objects.get(id=n.id).is_read)

    def test_mark_all_read(self):
        NotificationService.create('A', '', 'INFO', 'SYSTEM')
        NotificationService.create('B', '', 'SUCCESS', 'CRM')
        count = NotificationService.mark_all_read()
        self.assertEqual(count, 2)
        self.assertEqual(Notification.objects.filter(is_read=False).count(), 0)

    def test_get_unread_count(self):
        n1 = NotificationService.create('A', '', 'INFO', 'SYSTEM')
        NotificationService.create('B', '', 'INFO', 'SYSTEM')
        NotificationService.mark_read(n1.id)
        self.assertEqual(NotificationService.get_unread_count(), 1)

    def test_get_notifications_all(self):
        NotificationService.create('A', '', 'INFO', 'SYSTEM')
        NotificationService.create('B', '', 'SUCCESS', 'CRM')
        self.assertEqual(NotificationService.get_notifications().count(), 2)

    def test_get_notifications_filtered(self):
        NotificationService.create('A', '', 'INFO', 'SYSTEM')
        NotificationService.create('B', '', 'SUCCESS', 'CRM')
        qs = NotificationService.get_notifications(category='CRM')
        self.assertEqual(qs.count(), 1)
        self.assertEqual(qs.first().category, 'CRM')

    def test_delete_notification(self):
        n = NotificationService.create('Del', '', 'INFO', 'SYSTEM')
        result = NotificationService.delete(n.id)
        self.assertTrue(result)
        self.assertFalse(Notification.objects.filter(id=n.id).exists())

    def test_delete_nonexistent_returns_false(self):
        import uuid
        result = NotificationService.delete(uuid.uuid4())
        self.assertFalse(result)

    def test_delete_all_read(self):
        n1 = NotificationService.create('Read', '', 'INFO', 'SYSTEM')
        n2 = NotificationService.create('Unread', '', 'INFO', 'SYSTEM')
        NotificationService.mark_read(n1.id)
        count = NotificationService.delete_all_read()
        self.assertEqual(count, 1)
        self.assertFalse(Notification.objects.filter(id=n1.id).exists())
        self.assertTrue(Notification.objects.filter(id=n2.id).exists())

    def test_retention_max_notifications(self):
        # Bypass the service to avoid triggering retention on each create
        for i in range(MAX_NOTIFICATIONS + 5):
            Notification.objects.create(
                title=f'Notif {i}',
                message='',
                type='INFO',
                category='SYSTEM',
            )
        NotificationService._enforce_retention()
        self.assertLessEqual(Notification.objects.count(), MAX_NOTIFICATIONS)

    def test_retention_ttl(self):
        # Create a notification and backdate it beyond the TTL
        old = Notification.objects.create(
            title='Old Notification',
            message='',
            type='INFO',
            category='SYSTEM',
        )
        Notification.objects.filter(id=old.id).update(
            created_at=timezone.now() - timedelta(days=91)
        )
        NotificationService._enforce_retention()
        self.assertFalse(Notification.objects.filter(id=old.id).exists())

    def test_cleanup_old_notifications(self):
        recent = Notification.objects.create(title='Recent', message='', type='INFO', category='SYSTEM')
        old = Notification.objects.create(title='Old', message='', type='INFO', category='SYSTEM')
        Notification.objects.filter(id=old.id).update(
            created_at=timezone.now() - timedelta(days=91)
        )
        count = NotificationService.cleanup_old_notifications()
        self.assertEqual(count, 1)
        self.assertTrue(Notification.objects.filter(id=recent.id).exists())
        self.assertFalse(Notification.objects.filter(id=old.id).exists())


# =============================================================================
# API Tests
# =============================================================================

class NotificationAPITests(TestCase):

    def setUp(self):
        admin_group, _ = Group.objects.get_or_create(name='Admin')
        self.user = User.objects.create_user(
            username='adminuser',
            email='admin@test.com',
            password='testpass123',
        )
        self.user.groups.add(admin_group)

        self.non_admin = User.objects.create_user(
            username='regular',
            email='regular@test.com',
            password='testpass123',
        )

        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        self.n1 = Notification.objects.create(
            title='Test 1', message='Message 1', type='INFO', category='SYSTEM'
        )
        self.n2 = Notification.objects.create(
            title='Test 2', message='Message 2', type='SUCCESS', category='CRM'
        )

    def test_list_notifications(self):
        resp = self.client.get('/api/v1/admin/notifications/')
        self.assertEqual(resp.status_code, http_status.HTTP_200_OK)
        self.assertIn('results', resp.data)
        self.assertIn('available_categories', resp.data)

    def test_list_unauthenticated(self):
        anon = APIClient()
        resp = anon.get('/api/v1/admin/notifications/')
        self.assertEqual(resp.status_code, http_status.HTTP_401_UNAUTHORIZED)

    def test_list_non_admin_forbidden(self):
        client = APIClient()
        client.force_authenticate(user=self.non_admin)
        resp = client.get('/api/v1/admin/notifications/')
        self.assertEqual(resp.status_code, http_status.HTTP_403_FORBIDDEN)

    def test_list_category_filter(self):
        resp = self.client.get('/api/v1/admin/notifications/?category=CRM')
        self.assertEqual(resp.status_code, http_status.HTTP_200_OK)
        for item in resp.data['results']:
            self.assertEqual(item['category'], 'CRM')

    def test_unread_count(self):
        resp = self.client.get('/api/v1/admin/notifications/unread-count/')
        self.assertEqual(resp.status_code, http_status.HTTP_200_OK)
        self.assertIn('unread_count', resp.data)
        self.assertEqual(resp.data['unread_count'], 2)

    def test_notification_detail(self):
        resp = self.client.get(f'/api/v1/admin/notifications/{self.n1.id}/')
        self.assertEqual(resp.status_code, http_status.HTTP_200_OK)
        self.assertEqual(str(resp.data['id']), str(self.n1.id))
        self.assertIn('actor_name', resp.data)
        self.assertIn('recipient_name', resp.data)

    def test_mark_read(self):
        resp = self.client.patch(f'/api/v1/admin/notifications/{self.n1.id}/read/')
        self.assertEqual(resp.status_code, http_status.HTTP_200_OK)
        self.assertTrue(resp.data['is_read'])
        self.assertTrue(Notification.objects.get(id=self.n1.id).is_read)

    def test_mark_unread(self):
        NotificationService.mark_read(self.n1.id)
        resp = self.client.patch(f'/api/v1/admin/notifications/{self.n1.id}/unread/')
        self.assertEqual(resp.status_code, http_status.HTTP_200_OK)
        self.assertFalse(resp.data['is_read'])
        self.assertFalse(Notification.objects.get(id=self.n1.id).is_read)

    def test_mark_all_read(self):
        resp = self.client.patch('/api/v1/admin/notifications/read-all/')
        self.assertEqual(resp.status_code, http_status.HTTP_200_OK)
        self.assertIn('marked_read', resp.data)
        self.assertEqual(resp.data['marked_read'], 2)
        self.assertEqual(Notification.objects.filter(is_read=False).count(), 0)

    def test_delete_all_read(self):
        NotificationService.mark_all_read()
        resp = self.client.delete('/api/v1/admin/notifications/read/')
        self.assertEqual(resp.status_code, http_status.HTTP_200_OK)
        self.assertIn('deleted', resp.data)
        self.assertEqual(resp.data['deleted'], 2)
        self.assertEqual(Notification.objects.count(), 0)

    def test_mark_read_not_found(self):
        import uuid
        resp = self.client.patch(f'/api/v1/admin/notifications/{uuid.uuid4()}/read/')
        self.assertEqual(resp.status_code, http_status.HTTP_404_NOT_FOUND)
