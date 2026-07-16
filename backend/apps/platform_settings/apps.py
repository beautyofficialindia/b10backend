from django.apps import AppConfig

class PlatformSettingsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.platform_settings'
    verbose_name = 'Platform Settings'

    def ready(self):
        import apps.platform_settings.signals
