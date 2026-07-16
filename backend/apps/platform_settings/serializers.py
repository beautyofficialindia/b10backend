from rest_framework import serializers
from .models import PlatformSetting

class PlatformSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlatformSetting
        fields = '__all__'

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        if instance.is_sensitive and ret.get('value'):
            ret['value'] = '********'
        return ret

class PlatformSettingUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlatformSetting
        fields = ['value']

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        if instance.is_sensitive and ret.get('value'):
            ret['value'] = '********'
        return ret

class SettingsGroupResponseSerializer(serializers.Serializer):
    name = serializers.CharField()
    display_name = serializers.CharField()
    count = serializers.IntegerField()
    editable_count = serializers.IntegerField()

class InitializeSettingsResponseSerializer(serializers.Serializer):
    message = serializers.CharField()
    created = serializers.IntegerField()

class ResetSettingsRequestSerializer(serializers.Serializer):
    confirm = serializers.CharField(required=True)

    def validate_confirm(self, value):
        if value != "RESET_PLATFORM_SETTINGS":
            raise serializers.ValidationError("Invalid confirmation token.")
        return value

class ResetSettingsResponseSerializer(serializers.Serializer):
    message = serializers.CharField()
    reset_count = serializers.IntegerField()

class CacheRequestSerializer(serializers.Serializer):
    group = serializers.CharField(required=False, allow_null=True)
    key = serializers.CharField(required=False, allow_null=True)

class CacheResponseSerializer(serializers.Serializer):
    message = serializers.CharField()
    group = serializers.CharField(required=False, allow_null=True)
    key = serializers.CharField(required=False, allow_null=True)
