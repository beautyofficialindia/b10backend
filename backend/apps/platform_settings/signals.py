from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import PlatformSetting
from .services import SettingsService

@receiver(post_save, sender=PlatformSetting)
def clear_settings_cache_on_save(sender, instance, **kwargs):
    SettingsService.clear_cache(group=instance.group, key=instance.key)

@receiver(post_delete, sender=PlatformSetting)
def clear_settings_cache_on_delete(sender, instance, **kwargs):
    SettingsService.clear_cache(group=instance.group, key=instance.key)
