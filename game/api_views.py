from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_http_methods

from .live_chat import post_message, read_messages_since
from .timekeeping import next_reset_at, paris_now


def _no_store(response):
    response["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response["Pragma"] = "no-cache"
    return response


@require_GET
def version_status(request):
    now = paris_now()
    response = JsonResponse(
        {
            "version": settings.SOMRPG_VERSION,
            "paris_time": now.isoformat(),
            "next_reset": next_reset_at(now).isoformat(),
            "reset_hour": 22,
        }
    )
    return _no_store(response)


@require_http_methods(["GET", "POST"])
def live_chat(request):
    if not request.user.is_authenticated:
        return _no_store(JsonResponse({"error": "authentication_required"}, status=403))

    if request.method == "GET":
        try:
            since = float(request.GET.get("since", "0"))
        except (TypeError, ValueError):
            since = 0.0
        fresh = request.GET.get("fresh") == "1"
        now, messages = read_messages_since(since=since, fresh=fresh)
        return _no_store(JsonResponse({"now": now, "messages": messages}))

    profile = getattr(request.user, "discord_profile", None)
    display_name = profile.display_name if profile else request.user.get_username()
    ok, reason, message = post_message(request.user.pk, display_name, request.POST.get("message", ""))
    if not ok:
        status = 429 if reason == "rate" else 400
        return _no_store(JsonResponse({"error": reason}, status=status))
    return _no_store(JsonResponse({"message": message}, status=201))
