from rest_framework import generics, views, status, filters
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, OpenApiParameter
from django.db.models import Count, Q

from .models import PlatformSetting
from .constants import SettingGroup
from .services import SettingsService
from .serializers import (
    PlatformSettingSerializer,
    PlatformSettingUpdateSerializer,
    SettingsGroupResponseSerializer,
    InitializeSettingsResponseSerializer,
    ResetSettingsRequestSerializer,
    ResetSettingsResponseSerializer,
    CacheRequestSerializer,
    CacheResponseSerializer
)
from .permissions import (
    CanViewPlatformSettings,
    CanChangePlatformSettings,
    CanInitializePlatformSettings
)
from common.pagination import StandardPageNumberPagination

class AdminSettingsListAPIView(generics.ListAPIView):
    """List all platform settings with search, filtering, and ordering."""
    queryset = PlatformSetting.objects.all()
    serializer_class = PlatformSettingSerializer
    permission_classes = [CanViewPlatformSettings]
    pagination_class = StandardPageNumberPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    
    filterset_fields = ['group', 'is_editable', 'is_public', 'is_sensitive', 'value_type']
    search_fields = ['key', 'display_name', 'description']
    ordering_fields = ['group', 'display_order', 'display_name', 'created_at', 'updated_at']
    ordering = ['group', 'display_order', 'key']

    @extend_schema(
        summary="List Platform Settings",
        description="Retrieve a paginated list of all platform settings. Sensitive values are masked.",
        responses={200: PlatformSettingSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

class AdminSettingsGroupsAPIView(views.APIView):
    """List all setting groups with their counts."""
    permission_classes = [CanViewPlatformSettings]

    @extend_schema(
        summary="List Settings Groups",
        description="Get a list of all setting groups with total and editable counts.",
        responses={200: SettingsGroupResponseSerializer(many=True)}
    )
    def get(self, request):
        groups = PlatformSetting.objects.values('group').annotate(
            count=Count('id'),
            editable_count=Count('id', filter=Q(is_editable=True))
        )
        
        group_choices_dict = dict(SettingGroup.CHOICES)
        response_data = []
        for g in groups:
            group_name = g['group']
            response_data.append({
                'name': group_name,
                'display_name': group_choices_dict.get(group_name, group_name),
                'count': g['count'],
                'editable_count': g['editable_count']
            })
            
        serializer = SettingsGroupResponseSerializer(response_data, many=True)
        return Response(serializer.data)

class AdminSettingsByGroupAPIView(generics.ListAPIView):
    """List settings filtered by a specific group."""
    serializer_class = PlatformSettingSerializer
    permission_classes = [CanViewPlatformSettings]
    pagination_class = StandardPageNumberPagination

    def get_queryset(self):
        return PlatformSetting.objects.filter(group=self.kwargs['group'])

    @extend_schema(
        summary="List Settings by Group",
        description="Retrieve settings filtered by the provided group name.",
        responses={200: PlatformSettingSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

class AdminSettingDetailAPIView(generics.RetrieveUpdateAPIView):
    """Retrieve or update a specific platform setting."""
    queryset = PlatformSetting.objects.all()
    lookup_field = 'id'

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return PlatformSettingUpdateSerializer
        return PlatformSettingSerializer

    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH']:
            return [CanChangePlatformSettings()]
        return [CanViewPlatformSettings()]

    @extend_schema(
        summary="Retrieve a Setting",
        description="Get details of a single setting. Sensitive values are masked.",
        responses={200: PlatformSettingSerializer}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        summary="Update a Setting",
        description="Update the value of a single setting.",
        request=PlatformSettingUpdateSerializer,
        responses={200: PlatformSettingSerializer}
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

    @extend_schema(exclude=True)
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

class InitializeSettingsAPIView(views.APIView):
    """Initialize default settings."""
    permission_classes = [CanInitializePlatformSettings]

    @extend_schema(
        summary="Initialize Default Settings",
        description="Seed the database with default platform settings without overwriting existing ones.",
        responses={200: InitializeSettingsResponseSerializer}
    )
    def post(self, request):
        created_count = SettingsService.initialize_defaults(user=request.user)
        return Response({
            "message": "Settings initialized.",
            "created": created_count
        }, status=status.HTTP_200_OK)

class ResetSettingsAPIView(views.APIView):
    """Reset all default settings to their original values."""
    permission_classes = [CanInitializePlatformSettings]

    @extend_schema(
        summary="Reset Settings",
        description="Force reset all default settings to their original values. Requires a specific confirmation token.",
        request=ResetSettingsRequestSerializer,
        responses={200: ResetSettingsResponseSerializer}
    )
    def post(self, request):
        serializer = ResetSettingsRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        reset_count = SettingsService.reset_defaults(user=request.user)
        return Response({
            "message": "Settings reset successfully.",
            "reset_count": reset_count
        }, status=status.HTTP_200_OK)

class RefreshSettingsCacheAPIView(views.APIView):
    """Refresh the cache for settings."""
    permission_classes = [CanInitializePlatformSettings]

    @extend_schema(
        summary="Refresh Cache",
        description="Refresh the cache for all settings, a specific group, or a single setting.",
        request=CacheRequestSerializer,
        responses={200: CacheResponseSerializer}
    )
    def post(self, request):
        serializer = CacheRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        group = serializer.validated_data.get('group')
        key = serializer.validated_data.get('key')
        
        if group and key:
            SettingsService.refresh_cache(group, key)
            msg = f"Cache refreshed for setting {group}:{key}."
        elif group:
            SettingsService.clear_cache(group=group)
            msg = f"Cache cleared for group {group}. It will be rebuilt on next access."
        else:
            SettingsService.clear_cache()
            msg = "Global cache cleared. It will be rebuilt on next access."
            
        return Response({
            "message": msg,
            "group": group,
            "key": key
        }, status=status.HTTP_200_OK)

class ClearSettingsCacheAPIView(views.APIView):
    """Clear the cache for settings."""
    permission_classes = [CanInitializePlatformSettings]

    @extend_schema(
        summary="Clear Cache",
        description="Clear the cache for all settings, a specific group, or a single setting.",
        request=CacheRequestSerializer,
        responses={200: CacheResponseSerializer}
    )
    def post(self, request):
        serializer = CacheRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        group = serializer.validated_data.get('group')
        key = serializer.validated_data.get('key')
        
        SettingsService.clear_cache(group, key)
        
        if group and key:
            msg = f"Cache cleared for setting {group}:{key}."
        elif group:
            msg = f"Cache cleared for group {group}."
        else:
            msg = "Global cache cleared."
            
        return Response({
            "message": msg,
            "group": group,
            "key": key
        }, status=status.HTTP_200_OK)
