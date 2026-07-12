from rest_framework import serializers
from django.contrib.auth.models import User, Group
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['id', 'name']

class UserSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()
    groups = GroupSerializer(many=True, read_only=True)
    permissions = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role', 'groups', 'permissions', 'is_superuser', 'is_staff']

    def get_role(self, obj):
        group = obj.groups.first()
        return group.name if group else None

    def get_permissions(self, obj):
        return sorted(list(obj.get_all_permissions()))

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        
        group = self.user.groups.first()
        role = group.name if group else None
        
        data['user'] = {
            'id': self.user.id,
            'username': self.user.username,
            'email': self.user.email,
            'role': role
        }
        return data

class LogoutRequestSerializer(serializers.Serializer):
    refresh = serializers.CharField(help_text="Refresh token to blacklist")

class RefreshRequestSerializer(serializers.Serializer):
    refresh = serializers.CharField(help_text="Refresh token to get a new access token")

class TokenResponseSerializer(serializers.Serializer):
    access = serializers.CharField()
    refresh = serializers.CharField(required=False)

class LoginResponseSerializer(serializers.Serializer):
    access = serializers.CharField()
    refresh = serializers.CharField()
    user = serializers.DictField()

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True, allow_blank=False)
    new_password = serializers.CharField(required=True, allow_blank=False)

class ChangePasswordResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    message = serializers.CharField()

class UpdateProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'username']

    def validate(self, attrs):
        allowed_keys = {'first_name', 'last_name', 'email', 'username'}
        input_keys = set(self.initial_data.keys())
        forbidden_keys = input_keys - allowed_keys
        
        if forbidden_keys:
            errors = {key: ["This field cannot be updated."] for key in forbidden_keys}
            raise serializers.ValidationError(errors)
        return super().validate(attrs)
