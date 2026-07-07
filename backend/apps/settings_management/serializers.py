from rest_framework import serializers

from .models import Setting


class SettingSerializer(serializers.ModelSerializer):
    """Serializer for admin setting list/detail responses."""

    updated_by_username = serializers.SerializerMethodField()

    class Meta:
        model = Setting
        fields = [
            'id', 'category', 'key', 'value', 'description',
            'is_public', 'updated_at', 'updated_by_username',
        ]

    def get_updated_by_username(self, obj):
        if obj.updated_by:
            return obj.updated_by.username
        return None


class SettingPublicSerializer(serializers.ModelSerializer):
    """Serializer for public settings (no auth required)."""

    class Meta:
        model = Setting
        fields = ['category', 'key', 'value']


class SettingUpdateSerializer(serializers.Serializer):
    """Serializer for updating settings within a category (key-value pairs)."""

    settings = serializers.DictField(
        child=serializers.JSONField(allow_null=True),
        required=True,
    )
