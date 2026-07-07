from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from rest_framework.decorators import action
from rest_framework.mixins import (
    CreateModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
)
from rest_framework.viewsets import GenericViewSet
from rest_framework_simplejwt.authentication import JWTAuthentication

from apps.accounts.permissions import IsAdminUser
from common.pagination import StandardPageNumberPagination
from common.responses import success_response, error_response

from .serializers import (
    AuditLogSerializer,
    BulkActionSerializer,
    PasswordResetSerializer,
    UserCreateSerializer,
    UserDetailSerializer,
    UserListSerializer,
    UserUpdateSerializer,
)
from .services.user_service import UserService

User = get_user_model()


def _parse_bool(value):
    """Parse a query parameter string into a boolean or None."""
    if value is None:
        return None
    return value.lower() in ('true', '1', 'yes')


@extend_schema_view(
    list=extend_schema(
        summary="List backend users",
        description="Returns a paginated list of backend users with search, filtering, and ordering.",
        parameters=[
            OpenApiParameter(name='search', type=str, description='Search across username, email, first_name, last_name'),
            OpenApiParameter(name='ordering', type=str, description='Order by: username, email, date_joined, last_login, first_name, last_name (prefix with - for desc)'),
            OpenApiParameter(name='is_active', type=bool, description='Filter by active status'),
            OpenApiParameter(name='is_staff', type=bool, description='Filter by staff status'),
            OpenApiParameter(name='is_superuser', type=bool, description='Filter by superuser status'),
            OpenApiParameter(name='group', type=str, description='Filter by group name'),
            OpenApiParameter(name='date_joined_after', type=str, description='Filter: date_joined >= value (ISO 8601)'),
            OpenApiParameter(name='date_joined_before', type=str, description='Filter: date_joined <= value (ISO 8601)'),
            OpenApiParameter(name='last_login_after', type=str, description='Filter: last_login >= value (ISO 8601)'),
            OpenApiParameter(name='last_login_before', type=str, description='Filter: last_login <= value (ISO 8601)'),
        ],
    ),
    create=extend_schema(summary="Create a backend user"),
    retrieve=extend_schema(summary="Retrieve a backend user"),
    partial_update=extend_schema(summary="Update a backend user"),
)
class UserViewSet(
    CreateModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
    GenericViewSet,
):
    """
    ViewSet for managing backend users.
    Provides CRUD + custom actions. All business logic delegated to UserService.
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminUser]
    pagination_class = StandardPageNumberPagination
    http_method_names = ['get', 'post', 'patch', 'head', 'options']

    def get_serializer_class(self):
        if self.action == 'list':
            return UserListSerializer
        if self.action == 'create':
            return UserCreateSerializer
        if self.action == 'partial_update':
            return UserUpdateSerializer
        if self.action == 'reset_password':
            return PasswordResetSerializer
        if self.action in ('bulk_activate', 'bulk_deactivate'):
            return BulkActionSerializer
        if self.action == 'audit_log':
            return AuditLogSerializer
        return UserDetailSerializer

    def get_queryset(self):
        return User.objects.prefetch_related("groups").all()

    # ─── Standard CRUD ─────────────────────────────────────────────────

    def list(self, request):
        """List backend users with search, filtering, and ordering."""
        params = request.query_params

        try:
            queryset = UserService.list_users(
                search=params.get('search'),
                ordering=params.get('ordering'),
                is_active=_parse_bool(params.get('is_active')),
                is_staff=_parse_bool(params.get('is_staff')),
                is_superuser=_parse_bool(params.get('is_superuser')),
                group=params.get('group'),
                date_joined_after=params.get('date_joined_after'),
                date_joined_before=params.get('date_joined_before'),
                last_login_after=params.get('last_login_after'),
                last_login_before=params.get('last_login_before'),
            )
        except ValidationError as e:
            error_dict = e.message_dict if hasattr(e, 'message_dict') else {'detail': e.messages}
            return error_response(
                code='validation_error',
                message='Invalid filter parameter',
                details=error_dict,
                status=400,
            )

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = UserListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = UserListSerializer(queryset, many=True)
        return success_response(data=serializer.data)

    def create(self, request):
        """Create a new backend user."""
        serializer = UserCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=False)

        if serializer.errors:
            return error_response(
                code='validation_error',
                message='Validation failed',
                details=serializer.errors,
                status=400,
            )

        try:
            user = UserService.create_user(
                data=serializer.validated_data,
                actor=request.user,
            )
        except ValidationError as e:
            # Determine error code based on field
            error_dict = e.message_dict if hasattr(e, 'message_dict') else {'detail': e.messages}
            code = 'validation_error'
            message = 'Validation failed'
            if 'username' in error_dict:
                code = 'username_exists'
                message = error_dict['username'][0] if isinstance(error_dict['username'], list) else error_dict['username']
            elif 'email' in error_dict:
                code = 'email_exists'
                message = error_dict['email'][0] if isinstance(error_dict['email'], list) else error_dict['email']
            elif 'groups' in error_dict:
                code = 'invalid_groups'
                message = error_dict['groups'][0] if isinstance(error_dict['groups'], list) else error_dict['groups']
            elif 'password' in error_dict:
                code = 'password_invalid'
                message = 'Password does not meet requirements'

            return error_response(
                code=code,
                message=message,
                details=error_dict,
                status=400,
            )

        # Re-fetch with prefetch for serialization
        user = UserService.get_user(user.pk)
        detail_serializer = UserDetailSerializer(user)
        return success_response(
            data=detail_serializer.data,
            message='User created successfully',
            status=201,
        )

    def retrieve(self, request, pk=None):
        """Retrieve a single backend user by ID."""
        try:
            user = UserService.get_user(int(pk))
        except (User.DoesNotExist, ValueError, TypeError):
            return error_response(
                code='user_not_found',
                message=f'User with id {pk} not found',
                status=404,
            )

        serializer = UserDetailSerializer(user)
        return success_response(data=serializer.data)

    def partial_update(self, request, pk=None):
        """Update a backend user (PATCH)."""
        try:
            user = UserService.get_user(int(pk))
        except (User.DoesNotExist, ValueError, TypeError):
            return error_response(
                code='user_not_found',
                message=f'User with id {pk} not found',
                status=404,
            )

        serializer = UserUpdateSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=False)

        if serializer.errors:
            # Check if username rejection
            if 'username' in serializer.errors:
                return error_response(
                    code='username_not_editable',
                    message='Username cannot be modified after creation',
                    details=serializer.errors,
                    status=400,
                )
            return error_response(
                code='validation_error',
                message='Validation failed',
                details=serializer.errors,
                status=400,
            )

        try:
            user = UserService.update_user(
                user=user,
                data=serializer.validated_data,
                actor=request.user,
            )
        except ValidationError as e:
            error_dict = e.message_dict if hasattr(e, 'message_dict') else {'detail': e.messages}
            code = 'validation_error'
            message = 'Validation failed'
            if 'username' in error_dict:
                code = 'username_not_editable'
                message = 'Username cannot be modified after creation'
            elif 'email' in error_dict:
                code = 'email_exists'
                message = error_dict['email'][0] if isinstance(error_dict['email'], list) else error_dict['email']
            elif 'groups' in error_dict:
                code = 'invalid_groups'
                message = error_dict['groups'][0] if isinstance(error_dict['groups'], list) else error_dict['groups']
            elif 'is_superuser' in error_dict:
                code = 'last_superuser_protection'
                message = error_dict['is_superuser'][0] if isinstance(error_dict['is_superuser'], list) else error_dict['is_superuser']
            elif 'is_active' in error_dict:
                code = 'last_superuser_protection'
                message = error_dict['is_active'][0] if isinstance(error_dict['is_active'], list) else error_dict['is_active']

            return error_response(
                code=code,
                message=message,
                details=error_dict,
                status=400,
            )

        # Re-fetch with prefetch for serialization
        user = UserService.get_user(user.pk)
        detail_serializer = UserDetailSerializer(user)
        return success_response(data=detail_serializer.data, message='User updated successfully')

    # ─── Custom actions ────────────────────────────────────────────────

    @extend_schema(summary="Get current admin profile")
    @action(detail=False, methods=['get'], url_path='me', url_name='me')
    def me(self, request):
        """Returns the requesting admin's own profile."""
        user = UserService.get_user(request.user.pk)
        serializer = UserDetailSerializer(user)
        return success_response(data=serializer.data)

    @extend_schema(summary="Activate a backend user")
    @action(detail=True, methods=['post'], url_path='activate', url_name='activate')
    def activate(self, request, pk=None):
        """Activate a user (set is_active=True)."""
        try:
            user = UserService.get_user(int(pk))
        except (User.DoesNotExist, ValueError, TypeError):
            return error_response(
                code='user_not_found',
                message=f'User with id {pk} not found',
                status=404,
            )

        user = UserService.activate_user(user, actor=request.user)
        serializer = UserDetailSerializer(user)
        return success_response(data=serializer.data, message='User activated successfully')

    @extend_schema(summary="Deactivate a backend user")
    @action(detail=True, methods=['post'], url_path='deactivate', url_name='deactivate')
    def deactivate(self, request, pk=None):
        """Deactivate a user (set is_active=False)."""
        try:
            user = UserService.get_user(int(pk))
        except (User.DoesNotExist, ValueError, TypeError):
            return error_response(
                code='user_not_found',
                message=f'User with id {pk} not found',
                status=404,
            )

        try:
            user = UserService.deactivate_user(user, actor=request.user)
        except ValidationError as e:
            error_dict = e.message_dict if hasattr(e, 'message_dict') else {'detail': e.messages}
            detail_msg = error_dict.get('detail', ['Operation failed'])
            message = detail_msg[0] if isinstance(detail_msg, list) else detail_msg

            code = 'cannot_deactivate_self'
            if 'last active superuser' in message.lower():
                code = 'last_superuser_protection'

            return error_response(code=code, message=message, details=error_dict, status=400)

        serializer = UserDetailSerializer(user)
        return success_response(data=serializer.data, message='User deactivated successfully')

    @extend_schema(summary="Reset a backend user's password")
    @action(detail=True, methods=['post'], url_path='reset-password', url_name='reset-password')
    def reset_password(self, request, pk=None):
        """Reset a user's password."""
        try:
            user = UserService.get_user(int(pk))
        except (User.DoesNotExist, ValueError, TypeError):
            return error_response(
                code='user_not_found',
                message=f'User with id {pk} not found',
                status=404,
            )

        serializer = PasswordResetSerializer(data=request.data)
        serializer.is_valid(raise_exception=False)

        if serializer.errors:
            return error_response(
                code='validation_error',
                message='Validation failed',
                details=serializer.errors,
                status=400,
            )

        try:
            UserService.reset_password(
                user=user,
                password=serializer.validated_data['password'],
                actor=request.user,
            )
        except ValidationError as e:
            error_dict = e.message_dict if hasattr(e, 'message_dict') else {'detail': e.messages}
            return error_response(
                code='password_invalid',
                message='Password does not meet requirements',
                details=error_dict,
                status=400,
            )

        return success_response(message='Password reset successfully')

    @extend_schema(summary="Get audit log for a backend user")
    @action(detail=True, methods=['get'], url_path='audit-log', url_name='audit-log')
    def audit_log(self, request, pk=None):
        """Returns paginated audit log for a user."""
        # Verify user exists
        try:
            UserService.get_user(int(pk))
        except (User.DoesNotExist, ValueError, TypeError):
            return error_response(
                code='user_not_found',
                message=f'User with id {pk} not found',
                status=404,
            )

        queryset = UserService.get_audit_log(int(pk))
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = AuditLogSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = AuditLogSerializer(queryset, many=True)
        return success_response(data=serializer.data)

    @extend_schema(summary="Bulk activate backend users")
    @action(detail=False, methods=['post'], url_path='bulk-activate', url_name='bulk-activate')
    def bulk_activate(self, request):
        """Activate multiple users at once."""
        serializer = BulkActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=False)

        if serializer.errors:
            return error_response(
                code='validation_error',
                message='Validation failed',
                details=serializer.errors,
                status=400,
            )

        result = UserService.bulk_activate(
            user_ids=serializer.validated_data['user_ids'],
            actor=request.user,
        )
        return success_response(data=result, message='Bulk activation completed')

    @extend_schema(summary="Bulk deactivate backend users")
    @action(detail=False, methods=['post'], url_path='bulk-deactivate', url_name='bulk-deactivate')
    def bulk_deactivate(self, request):
        """Deactivate multiple users at once."""
        serializer = BulkActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=False)

        if serializer.errors:
            return error_response(
                code='validation_error',
                message='Validation failed',
                details=serializer.errors,
                status=400,
            )

        result = UserService.bulk_deactivate(
            user_ids=serializer.validated_data['user_ids'],
            actor=request.user,
        )
        return success_response(data=result, message='Bulk deactivation completed')
