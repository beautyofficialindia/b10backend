from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import UserAuditLog

User = get_user_model()


class UserListSerializer(serializers.ModelSerializer):
    """Serializer for user list responses."""

    groups = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'is_active', 'is_staff', 'is_superuser', 'groups',
            'date_joined', 'last_login',
        ]

    def get_groups(self, obj):
        return list(obj.groups.values_list('name', flat=True))


class UserDetailSerializer(UserListSerializer):
    """Serializer for user detail responses — adds permissions."""

    permissions = serializers.SerializerMethodField()

    class Meta(UserListSerializer.Meta):
        fields = UserListSerializer.Meta.fields + ['permissions']

    def get_permissions(self, obj):
        return sorted(obj.get_all_permissions())


class UserCreateSerializer(serializers.Serializer):
    """Serializer for user creation requests."""

    username = serializers.CharField(max_length=150, required=True)
    email = serializers.EmailField(required=True)
    first_name = serializers.CharField(max_length=150, required=False, default='')
    last_name = serializers.CharField(max_length=150, required=False, default='')
    password = serializers.CharField(write_only=True, required=True)
    groups = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        default=list,
    )
    is_active = serializers.BooleanField(required=False, default=True)
    is_staff = serializers.BooleanField(required=False, default=True)
    is_superuser = serializers.BooleanField(required=False, default=False)

    def validate_username(self, value):
        """Validate username format (Django default: alphanumeric + @.+-_)."""
        import re
        if not re.match(r'^[\w.@+-]+$', value):
            raise serializers.ValidationError(
                "Username may only contain letters, digits, and @/./+/-/_ characters."
            )
        return value

    def validate_email(self, value):
        """Normalize email to lowercase and strip whitespace."""
        return value.strip().lower()


class UserUpdateSerializer(serializers.Serializer):
    """Serializer for user update (PATCH) requests."""

    first_name = serializers.CharField(max_length=150, required=False)
    last_name = serializers.CharField(max_length=150, required=False)
    email = serializers.EmailField(required=False)
    groups = serializers.ListField(
        child=serializers.CharField(),
        required=False,
    )
    is_active = serializers.BooleanField(required=False)
    is_staff = serializers.BooleanField(required=False)
    is_superuser = serializers.BooleanField(required=False)

    def validate_email(self, value):
        """Normalize email to lowercase and strip whitespace."""
        return value.strip().lower()

    def validate(self, attrs):
        """Reject username field if included in request data."""
        request = self.context.get('request')
        if request and 'username' in request.data:
            raise serializers.ValidationError(
                {'username': 'Username cannot be modified after creation.'}
            )
        return attrs


class PasswordResetSerializer(serializers.Serializer):
    """Serializer for password reset requests."""

    password = serializers.CharField(write_only=True, required=True)


class BulkActionSerializer(serializers.Serializer):
    """Serializer for bulk activate/deactivate requests."""

    user_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=True,
        allow_empty=False,
    )


class AuditLogSerializer(serializers.ModelSerializer):
    """Serializer for audit log responses."""

    actor_username = serializers.SerializerMethodField()

    class Meta:
        model = UserAuditLog
        fields = [
            'id', 'actor', 'actor_username', 'target_user',
            'action', 'description', 'metadata', 'created_at',
        ]

    def get_actor_username(self, obj):
        if obj.actor:
            return obj.actor.username
        return None
