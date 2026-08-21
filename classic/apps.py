from django.apps import AppConfig


class _GameTimezoneProxy:
    """Keep django timezone helpers, but make localdate follow the SomRPG 22:00 Paris day."""

    def __init__(self, django_timezone, game_day_key):
        self._django_timezone = django_timezone
        self._game_day_key = game_day_key

    def __getattr__(self, name):
        return getattr(self._django_timezone, name)

    def localdate(self, value=None, timezone=None):
        return self._game_day_key(value)


class ClassicConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "classic"
    verbose_name = "SomRPG Classic Systems"

    def ready(self):
        from django.utils import timezone as django_timezone

        from game.timekeeping import game_day_key
        from . import services, signals  # noqa: F401

        services.timezone = _GameTimezoneProxy(django_timezone, game_day_key)
