from django.apps import AppConfig


class TaggerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tagger'

    def ready(self):
        from .settings import TAGGER_SETTINGS
        from django.conf import settings
        from .forms import SettingsForm

        settings.DEFAULT_SETTINGS.update(TAGGER_SETTINGS)
