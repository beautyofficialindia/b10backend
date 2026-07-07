from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from rest_framework.decorators import action
from rest_framework.viewsets import GenericViewSet
from rest_framework_simplejwt.authentication import JWTAuthentication

from apps.accounts.permissions import IsAdminUser
from common.pagination import StandardPageNumberPagination
from common.responses import success_response, error_response

from .serializers import (
    PermissionCodenamesSerializer,
    PermissionSerializer,
    RoleCreateSerializer,
    RoleDetailSerializer,
    RoleListSerializer,
    RoleUpdateSerializer,
    RoleUserSerializer,
    UserIdsSerializer,
)
from .services.role_service import RoleService


@extend_schema_view(
    list=extend_schema(summary="List roles", parameters=[
        OpenApiParameter(name='search', type=str, description='Search by role name'),
        OpenApiParameter(name='ordering', type=str, description='Order by: name, id (prefix with - for desc)'),
    ]),
    create=extend_schema(summary="Create a role"),
    retrieve=extend_schema(summary="Retrieve a role"),
    partial_update=extend_schema(summary="Update a role"),
    destroy=extend_schema(summary="Delete a role"),
)
class RoleViewSet(GenericViewSet):
    """ViewSet for managing roles. All logic delegated to RoleService."""

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminUser]
    pagination_class = StandardPageNumberPagination
    http_method_names = ['get', 'post', 'patch', 'put', 'delete', 'head', 'options']

    def get_serializer_class(self):
        if self.action == 'list':
            return RoleListSerializer
        if self.action == 'create':
            return RoleCreateSerializer
        if self.action == 'partial_update':
            return RoleUpdateSerializer
        if self.action in ('set_permissions', 'assign_permissions', 'remove_permissions'):
            return PermissionCodenamesSerializer
        if self.action in ('add_users', 'remove_users', 'assign_users'):
            return UserIdsSerializer
        if self.action == 'role_users':
            return RoleUserSerializer
        return RoleDetailSerializer

    def get_queryset(self):
        return Group.objects.all()

    # ─── CRUD ──────────────────────────────────────────────────────────

    def list(self, request):
        params = request.query_params
        queryset = RoleService.list_roles(
            search=params.get('search'),
            ordering=params.get('ordering'),
        )
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = RoleListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = RoleListSerializer(queryset, many=True)
        return success_response(data=serializer.data)

    def create(self, request):
        serializer = RoleCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response('validation_error', 'Validation failed', serializer.errors, 400)

        try:
            role = RoleService.create_role(
                name=serializer.validated_data['name'],
                permissions=serializer.validated_data.get('permissions', []),
                actor=request.user,
            )
        except ValidationError as e:
            error_dict = e.message_dict if hasattr(e, 'message_dict') else {'detail': e.messages}
            code = 'role_name_exists' if 'name' in error_dict else 'invalid_permissions'
            msg = list(error_dict.values())[0]
            msg = msg[0] if isinstance(msg, list) else msg
            return error_response(code, msg, error_dict, 400)

        detail = RoleDetailSerializer(role)
        return success_response(data=detail.data, message='Role created successfully', status=201)

    def retrieve(self, request, pk=None):
        try:
            role = RoleService.get_role(int(pk))
        except (Group.DoesNotExist, ValueError, TypeError):
            return error_response('role_not_found', f'Role with id {pk} not found', status=404)
        return success_response(data=RoleDetailSerializer(role).data)

    def partial_update(self, request, pk=None):
        try:
            role = RoleService.get_role(int(pk))
        except (Group.DoesNotExist, ValueError, TypeError):
            return error_response('role_not_found', f'Role with id {pk} not found', status=404)

        serializer = RoleUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response('validation_error', 'Validation failed', serializer.errors, 400)

        try:
            role = RoleService.update_role(role, serializer.validated_data['name'], actor=request.user)
        except ValidationError as e:
            error_dict = e.message_dict if hasattr(e, 'message_dict') else {'detail': e.messages}
            msg = list(error_dict.values())[0]
            msg = msg[0] if isinstance(msg, list) else msg
            return error_response('role_name_exists', msg, error_dict, 400)

        return success_response(data=RoleDetailSerializer(role).data, message='Role updated successfully')

    def destroy(self, request, pk=None):
        try:
            role = RoleService.get_role(int(pk))
        except (Group.DoesNotExist, ValueError, TypeError):
            return error_response('role_not_found', f'Role with id {pk} not found', status=404)

        try:
            RoleService.delete_role(role, actor=request.user)
        except ValidationError as e:
            error_dict = e.message_dict if hasattr(e, 'message_dict') else {'detail': e.messages}
            msg = list(error_dict.values())[0]
            msg = msg[0] if isinstance(msg, list) else msg
            return error_response('role_protected', msg, error_dict, 400)

        return success_response(message='Role deleted successfully', status=204)

    # ─── Permissions ───────────────────────────────────────────────────

    @extend_schema(summary="List all available permissions")
    @action(detail=False, methods=['get'], url_path='permissions', url_name='available-permissions')
    def available_permissions(self, request):
        perms = RoleService.list_available_permissions()
        serializer = PermissionSerializer(perms, many=True)
        return success_response(data=serializer.data)

    @extend_schema(summary="Get role permissions")
    @action(detail=True, methods=['get'], url_path='permissions', url_name='role-permissions')
    def get_permissions_action(self, request, pk=None):
        try:
            role = RoleService.get_role(int(pk))
        except (Group.DoesNotExist, ValueError, TypeError):
            return error_response('role_not_found', f'Role with id {pk} not found', status=404)
        perms = role.permissions.select_related('content_type').all()
        serializer = PermissionSerializer(perms, many=True)
        return success_response(data=serializer.data)

    @extend_schema(summary="Set role permissions (replace all)")
    @action(detail=True, methods=['put'], url_path='set-permissions', url_name='set-permissions')
    def set_permissions(self, request, pk=None):
        try:
            role = RoleService.get_role(int(pk))
        except (Group.DoesNotExist, ValueError, TypeError):
            return error_response('role_not_found', f'Role with id {pk} not found', status=404)

        serializer = PermissionCodenamesSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response('validation_error', 'Validation failed', serializer.errors, 400)

        try:
            role = RoleService.set_permissions(role, serializer.validated_data['permissions'], actor=request.user)
        except ValidationError as e:
            error_dict = e.message_dict if hasattr(e, 'message_dict') else {'detail': e.messages}
            msg = list(error_dict.values())[0]
            msg = msg[0] if isinstance(msg, list) else msg
            return error_response('invalid_permissions', msg, error_dict, 400)

        return success_response(data=RoleDetailSerializer(role).data, message='Permissions updated')

    @extend_schema(summary="Assign permissions to role")
    @action(detail=True, methods=['post'], url_path='assign-permissions', url_name='assign-permissions')
    def assign_permissions(self, request, pk=None):
        try:
            role = RoleService.get_role(int(pk))
        except (Group.DoesNotExist, ValueError, TypeError):
            return error_response('role_not_found', f'Role with id {pk} not found', status=404)

        serializer = PermissionCodenamesSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response('validation_error', 'Validation failed', serializer.errors, 400)

        try:
            perm_objects = RoleService._validate_permissions(serializer.validated_data['permissions'])
        except ValidationError as e:
            error_dict = e.message_dict if hasattr(e, 'message_dict') else {'detail': e.messages}
            msg = list(error_dict.values())[0]
            msg = msg[0] if isinstance(msg, list) else msg
            return error_response('invalid_permissions', msg, error_dict, 400)

        role.permissions.add(*perm_objects)

        RoleService._create_audit_log(
            actor=request.user,
            action='role_permissions_changed',
            description=f"Assigned permissions to role '{role.name}'",
            metadata={'role_id': role.pk, 'added': serializer.validated_data['permissions']},
        )
        return success_response(data=RoleDetailSerializer(role).data, message='Permissions assigned')

    @extend_schema(summary="Remove permissions from role")
    @action(detail=True, methods=['post'], url_path='remove-permissions', url_name='remove-permissions')
    def remove_permissions(self, request, pk=None):
        try:
            role = RoleService.get_role(int(pk))
        except (Group.DoesNotExist, ValueError, TypeError):
            return error_response('role_not_found', f'Role with id {pk} not found', status=404)

        serializer = PermissionCodenamesSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response('validation_error', 'Validation failed', serializer.errors, 400)

        try:
            perm_objects = RoleService._validate_permissions(serializer.validated_data['permissions'])
        except ValidationError as e:
            error_dict = e.message_dict if hasattr(e, 'message_dict') else {'detail': e.messages}
            msg = list(error_dict.values())[0]
            msg = msg[0] if isinstance(msg, list) else msg
            return error_response('invalid_permissions', msg, error_dict, 400)

        role.permissions.remove(*perm_objects)

        RoleService._create_audit_log(
            actor=request.user,
            action='role_permissions_changed',
            description=f"Removed permissions from role '{role.name}'",
            metadata={'role_id': role.pk, 'removed': serializer.validated_data['permissions']},
        )
        return success_response(data=RoleDetailSerializer(role).data, message='Permissions removed')

    # ─── User membership ───────────────────────────────────────────────

    @extend_schema(summary="List users in a role", parameters=[
        OpenApiParameter(name='search', type=str, description='Search users'),
    ])
    @action(detail=True, methods=['get'], url_path='users', url_name='role-users')
    def role_users(self, request, pk=None):
        try:
            role = RoleService.get_role(int(pk))
        except (Group.DoesNotExist, ValueError, TypeError):
            return error_response('role_not_found', f'Role with id {pk} not found', status=404)

        queryset = RoleService.list_role_users(role, search=request.query_params.get('search'))
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = RoleUserSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = RoleUserSerializer(queryset, many=True)
        return success_response(data=serializer.data)

    @extend_schema(summary="Add users to a role")
    @action(detail=True, methods=['post'], url_path='assign-users', url_name='assign-users')
    def add_users(self, request, pk=None):
        try:
            role = RoleService.get_role(int(pk))
        except (Group.DoesNotExist, ValueError, TypeError):
            return error_response('role_not_found', f'Role with id {pk} not found', status=404)

        serializer = UserIdsSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response('validation_error', 'Validation failed', serializer.errors, 400)

        result = RoleService.add_users(role, serializer.validated_data['user_ids'], actor=request.user)
        return success_response(data=result, message='Users assigned to role')

    @extend_schema(summary="Remove users from a role")
    @action(detail=True, methods=['post'], url_path='remove-users', url_name='remove-users')
    def remove_users(self, request, pk=None):
        try:
            role = RoleService.get_role(int(pk))
        except (Group.DoesNotExist, ValueError, TypeError):
            return error_response('role_not_found', f'Role with id {pk} not found', status=404)

        serializer = UserIdsSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response('validation_error', 'Validation failed', serializer.errors, 400)

        try:
            result = RoleService.remove_users(role, serializer.validated_data['user_ids'], actor=request.user)
        except ValidationError as e:
            error_dict = e.message_dict if hasattr(e, 'message_dict') else {'detail': e.messages}
            msg = list(error_dict.values())[0]
            msg = msg[0] if isinstance(msg, list) else msg
            return error_response('last_superuser_protection', msg, error_dict, 400)

        return success_response(data=result, message='Users removed from role')
