from rest_framework.views import APIView
from rest_framework.throttling import AnonRateThrottle

from apps.accounts.permissions import IsAdminUser
from rest_framework import viewsets

from apps.knowledge_base.models import KnowledgeEntry, Category, Tag
from apps.knowledge_base.serializers import (
    KnowledgeEntryDetailSerializer,
    KnowledgeEntryListSerializer,
    KnowledgeEntryWriteSerializer,
    CategorySerializer,
    TagSerializer,
)
from apps.knowledge_base.services.knowledge_service import KnowledgeService
from common.pagination import StandardPageNumberPagination
from common.responses import error_response, success_response


# ─── Public Views ───────────────────────────────────────────────────────────────


class PublicKnowledgeListView(APIView):
    authentication_classes = []
    permission_classes = []
    throttle_classes = [AnonRateThrottle]

    def get(self, request):
        category = request.query_params.get('category')
        search = request.query_params.get('search')

        entries = KnowledgeService.list_entries(
            category=category,
            search=search,
            status='published',
            include_deleted=False,
        )

        paginator = StandardPageNumberPagination()
        page = paginator.paginate_queryset(entries, request)
        if page is not None:
            serializer = KnowledgeEntryListSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        serializer = KnowledgeEntryListSerializer(entries, many=True)
        return success_response(data=serializer.data)


class PublicKnowledgeDetailView(APIView):
    authentication_classes = []
    permission_classes = []
    throttle_classes = [AnonRateThrottle]

    def get(self, request, slug):
        try:
            entry = KnowledgeEntry.objects.get(
                slug=slug, status='published', is_deleted=False
            )
        except KnowledgeEntry.DoesNotExist:
            return error_response(
                code='NOT_FOUND_RESOURCE',
                message='Knowledge entry not found.',
                status=404,
            )

        serializer = KnowledgeEntryDetailSerializer(entry)
        return success_response(data=serializer.data)


# ─── Admin Views ────────────────────────────────────────────────────────────────

class CategoryViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminUser]
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    pagination_class = StandardPageNumberPagination
    search_fields = ['name', 'slug']


class TagViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminUser]
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = StandardPageNumberPagination
    search_fields = ['name', 'slug']


class AdminKnowledgeListCreateView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        category = request.query_params.get('category')
        status = request.query_params.get('status')
        search = request.query_params.get('search')
        ordering = request.query_params.get('ordering')

        entries = KnowledgeService.list_entries(
            category=category,
            search=search,
            status=status,
            include_deleted=False,
            ordering=ordering,
        )

        paginator = StandardPageNumberPagination()
        page = paginator.paginate_queryset(entries, request)
        if page is not None:
            serializer = KnowledgeEntryListSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        serializer = KnowledgeEntryListSerializer(entries, many=True)
        return success_response(data=serializer.data)

    def post(self, request):
        serializer = KnowledgeEntryWriteSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(
                code='VALIDATION_ERROR',
                message='Invalid input.',
                details=serializer.errors,
                status=400,
            )

        try:
            entry = KnowledgeService.create_entry(
                data=serializer.validated_data,
                user=request.user,
            )
        except ValueError as e:
            return error_response(
                code='VALIDATION_ERROR',
                message=str(e),
                status=400,
            )

        response_serializer = KnowledgeEntryDetailSerializer(entry)
        return success_response(data=response_serializer.data, status=201)


class AdminKnowledgeDetailView(APIView):
    permission_classes = [IsAdminUser]

    def _get_entry(self, pk):
        try:
            return KnowledgeService.get_entry(pk, include_deleted=False)
        except KnowledgeEntry.DoesNotExist:
            return None

    def get(self, request, pk):
        entry = self._get_entry(pk)
        if entry is None:
            return error_response(
                code='NOT_FOUND_RESOURCE',
                message='Knowledge entry not found.',
                status=404,
            )
        serializer = KnowledgeEntryDetailSerializer(entry)
        return success_response(data=serializer.data)

    def patch(self, request, pk):
        entry = self._get_entry(pk)
        if entry is None:
            return error_response(
                code='NOT_FOUND_RESOURCE',
                message='Knowledge entry not found.',
                status=404,
            )

        serializer = KnowledgeEntryWriteSerializer(data=request.data, partial=True)
        if not serializer.is_valid():
            return error_response(
                code='VALIDATION_ERROR',
                message='Invalid input.',
                details=serializer.errors,
                status=400,
            )

        try:
            entry = KnowledgeService.update_entry(
                entry=entry,
                data=serializer.validated_data,
                user=request.user,
            )
        except ValueError as e:
            return error_response(
                code='VALIDATION_ERROR',
                message=str(e),
                status=400,
            )

        response_serializer = KnowledgeEntryDetailSerializer(entry)
        return success_response(data=response_serializer.data)

    def delete(self, request, pk):
        entry = self._get_entry(pk)
        if entry is None:
            return error_response(
                code='NOT_FOUND_RESOURCE',
                message='Knowledge entry not found.',
                status=404,
            )

        KnowledgeService.delete_entry(entry, request.user)
        return success_response(data={}, status=204)


class AdminKnowledgePublishView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, pk):
        try:
            entry = KnowledgeService.get_entry(pk, include_deleted=False)
        except KnowledgeEntry.DoesNotExist:
            return error_response(
                code='NOT_FOUND_RESOURCE',
                message='Knowledge entry not found.',
                status=404,
            )

        entry = KnowledgeService.publish_entry(entry, request.user)
        serializer = KnowledgeEntryDetailSerializer(entry)
        return success_response(data=serializer.data)


class AdminKnowledgeUnpublishView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, pk):
        try:
            entry = KnowledgeService.get_entry(pk, include_deleted=False)
        except KnowledgeEntry.DoesNotExist:
            return error_response(
                code='NOT_FOUND_RESOURCE',
                message='Knowledge entry not found.',
                status=404,
            )

        entry = KnowledgeService.unpublish_entry(entry, request.user)
        serializer = KnowledgeEntryDetailSerializer(entry)
        return success_response(data=serializer.data)


class AdminKnowledgeArchiveView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, pk):
        try:
            entry = KnowledgeService.get_entry(pk, include_deleted=False)
        except KnowledgeEntry.DoesNotExist:
            return error_response(
                code='NOT_FOUND_RESOURCE',
                message='Knowledge entry not found.',
                status=404,
            )

        entry = KnowledgeService.archive_entry(entry, request.user)
        serializer = KnowledgeEntryDetailSerializer(entry)
        return success_response(data=serializer.data)


class AdminKnowledgeRestoreView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, pk):
        try:
            entry = KnowledgeEntry.objects.get(pk=pk, is_deleted=True)
        except KnowledgeEntry.DoesNotExist:
            return error_response(
                code='NOT_FOUND_RESOURCE',
                message='No soft-deleted entry found with this ID.',
                status=404,
            )

        entry = KnowledgeService.restore_entry(entry, request.user)
        serializer = KnowledgeEntryDetailSerializer(entry)
        return success_response(data=serializer.data)
