from django.core.exceptions import ValidationError
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
from rest_framework_simplejwt.authentication import JWTAuthentication

from apps.accounts.permissions import IsAdminUser
from common.responses import success_response, error_response

from .serializers import SettingPublicSerializer, SettingSerializer, SettingUpdateSerializer
from .services.settings_service import SettingsService


class SettingsAdminViewSet(GenericViewSet):
    """Admin endpoints for settings management. All logic delegated to SettingsService."""

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminUser]

    @extend_schema(
        summary="List all settings",
        parameters=[
            OpenApiParameter(name='search', type=str, description='Search by key or description'),
            OpenApiParameter(name='category', type=str, description='Filter by category'),
        ],
    )
    def list(self, request):
        params = request.query_params
        try:
            queryset = SettingsService.list_settings(
                search=params.get('search'),
                category=params.get('category'),
            )
        except ValidationError as e:
            error_dict = e.message_dict if hasattr(e, 'message_dict') else {'detail': e.messages}
            msg = list(error_dict.values())[0]
            msg = msg[0] if isinstance(msg, list) else msg
            return error_response('invalid_category', msg, error_dict, 400)

        # Mask secrets before serializing
        settings_data = []
        for setting in queryset:
            data = SettingSerializer(setting).data
            if setting.category == 'INTEGRATIONS':
                data['value'] = SettingsService.mask_secret_value(setting)
            settings_data.append(data)

        return success_response(data=settings_data)

    @extend_schema(summary="Get settings by category")
    def retrieve_category(self, request, category=None):
        try:
            queryset = SettingsService.get_category_settings(category)
        except ValidationError as e:
            error_dict = e.message_dict if hasattr(e, 'message_dict') else {'detail': e.messages}
            msg = list(error_dict.values())[0]
            msg = msg[0] if isinstance(msg, list) else msg
            return error_response('invalid_category', msg, error_dict, 400)

        settings_data = []
        for setting in queryset:
            data = SettingSerializer(setting).data
            if setting.category == 'INTEGRATIONS':
                data['value'] = SettingsService.mask_secret_value(setting)
            settings_data.append(data)

        return success_response(data=settings_data)

    @extend_schema(summary="Update settings by category")
    def update_category(self, request, category=None):
        serializer = SettingUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response('validation_error', 'Validation failed', serializer.errors, 400)

        try:
            SettingsService.update_category_settings(
                category=category,
                data=serializer.validated_data['settings'],
                actor=request.user,
            )
        except ValidationError as e:
            error_dict = e.message_dict if hasattr(e, 'message_dict') else {'detail': e.messages}
            msg = list(error_dict.values())[0]
            msg = msg[0] if isinstance(msg, list) else msg
            code = 'invalid_category' if 'category' in error_dict else 'validation_error'
            return error_response(code, msg, error_dict, 400)

        # Return updated category
        queryset = SettingsService.get_category_settings(category)
        settings_data = []
        for setting in queryset:
            data = SettingSerializer(setting).data
            if setting.category == 'INTEGRATIONS':
                data['value'] = SettingsService.mask_secret_value(setting)
            settings_data.append(data)

        return success_response(data=settings_data, message='Settings updated successfully')


class PublicSettingsView(APIView):
    """Public endpoint for frontend-consumable settings. No auth required."""

    authentication_classes = []
    permission_classes = [AllowAny]

    @extend_schema(summary="Get public settings (no auth required)")
    def get(self, request):
        queryset = SettingsService.get_public_settings()
        serializer = SettingPublicSerializer(queryset, many=True)
        return success_response(data=serializer.data)
