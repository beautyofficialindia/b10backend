from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from rest_framework import serializers

User = get_user_model()


class RoleListSerializer(serializers.ModelSerializer):
    """Serializer for role list responses."""

    permissions_count = serializers.IntegerField(read_only=True)
    users_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Group
        fields = ['id', 'name', 'permissions_count', 'users_count']


class PermissionSerializer(serializers.ModelSerializer):
    """Serializer for permission objects."""

    content_type = serializers.SerializerMethodField()

    class Meta:
        model = Permission
        fields = ['id', 'codename', 'name', 'content_type']

    def get_content_type(self, obj):
        return f"{obj.content_type.app_label}.{obj.content_type.model}"


class RoleDetailSerializer(serializers.ModelSerializer):
    """Serializer for role detail responses."""

    permissions = serializers.SerializerMethodField()
    users_count = serializers.SerializerMethodField()

    class Meta:
        model = Group
        fields = ['id', 'name', 'permissions', 'users_count']

    def get_permissions(self, obj):
        return PermissionSerializer(obj.permissions.select_related('content_type'), many=True).data

    def get_users_count(self, obj):
        return obj.user_set.count()


class RoleCreateSerializer(serializers.Serializer):
    """Serializer for role creation requests."""

    name = serializers.CharField(max_length=150, required=True)
    permissions = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        default=list,
    )


class RoleUpdateSerializer(serializers.Serializer):
    """Serializer for role update (PATCH) requests."""

    name = serializers.CharField(max_length=150, required=True)


class PermissionCodenamesSerializer(serializers.Serializer):
    """Serializer for setting permissions on a role."""

    permissions = serializers.ListField(
        child=serializers.CharField(),
        required=True,
        allow_empty=True,
    )


class RoleUserSerializer(serializers.ModelSerializer):
    """Serializer for users in a role."""

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'is_active']


class UserIdsSerializer(serializers.Serializer):
    """Serializer for adding/removing users from a role."""

    user_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=True,
        allow_empty=False,
    )
