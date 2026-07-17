from django.db.models import Count
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404

from .models import Notification
from .serializers import NotificationSerializer
from .permissions import CanViewNotification, CanChangeNotification, CanDeleteNotification
from .services import NotificationService


class NotificationPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class NotificationListView(ListAPIView):
    """
    GET /api/v1/admin/notifications/

    Returns paginated notifications with an additional `available_categories`
    field — a list of {category, count} objects for only the categories that
    currently have notifications. Used by the frontend to render dynamic filter tabs.

    Query params:
        ?category=CRM   — filter by category
    """
    permission_classes = [CanViewNotification]
    serializer_class = NotificationSerializer
    pagination_class = NotificationPagination

    def get_queryset(self):
        category = self.request.query_params.get('category')
        return NotificationService.get_notifications(category=category)

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        # Attach available categories (always from the full unfiltered set)
        available = (
            Notification.objects
            .values('category')
            .annotate(count=Count('id'))
            .order_by('category')
        )
        response.data['available_categories'] = list(available)
        return response


class NotificationDetailView(RetrieveAPIView):
    """GET /api/v1/admin/notifications/{id}/"""
    permission_classes = [CanViewNotification]
    serializer_class = NotificationSerializer
    queryset = Notification.objects.select_related('actor', 'recipient').all()
    lookup_field = 'id'


class NotificationMarkReadView(APIView):
    """PATCH /api/v1/admin/notifications/{id}/read/"""
    permission_classes = [CanChangeNotification]

    def patch(self, request, id):
        get_object_or_404(Notification, id=id)
        notification = NotificationService.mark_read(id)
        return Response(NotificationSerializer(notification).data)


class NotificationMarkUnreadView(APIView):
    """PATCH /api/v1/admin/notifications/{id}/unread/"""
    permission_classes = [CanChangeNotification]

    def patch(self, request, id):
        get_object_or_404(Notification, id=id)
        notification = NotificationService.mark_unread(id)
        return Response(NotificationSerializer(notification).data)


class NotificationMarkAllReadView(APIView):
    """PATCH /api/v1/admin/notifications/read-all/"""
    permission_classes = [CanChangeNotification]

    def patch(self, request):
        count = NotificationService.mark_all_read()
        return Response({'marked_read': count})


class NotificationDeleteReadView(APIView):
    """DELETE /api/v1/admin/notifications/read/"""
    permission_classes = [CanDeleteNotification]

    def delete(self, request):
        count = NotificationService.delete_all_read()
        return Response({'deleted': count}, status=status.HTTP_200_OK)


class NotificationUnreadCountView(APIView):
    """GET /api/v1/admin/notifications/unread-count/"""
    permission_classes = [CanViewNotification]

    def get(self, request):
        count = NotificationService.get_unread_count()
        return Response({'unread_count': count})
