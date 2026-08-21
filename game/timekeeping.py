from datetime import timedelta
from zoneinfo import ZoneInfo

from django.utils import timezone


PARIS_TZ = ZoneInfo("Europe/Paris")
RESET_HOUR = 22


def paris_now(now=None):
    current = now or timezone.now()
    if timezone.is_naive(current):
        current = timezone.make_aware(current, timezone.utc)
    return current.astimezone(PARIS_TZ)


def game_day_key(now=None):
    """Return the logical SomRPG day, which changes at 22:00 Europe/Paris."""
    return (paris_now(now) - timedelta(hours=RESET_HOUR)).date()


def next_reset_at(now=None):
    local = paris_now(now)
    reset = local.replace(hour=RESET_HOUR, minute=0, second=0, microsecond=0)
    if local >= reset:
        reset += timedelta(days=1)
    return reset
