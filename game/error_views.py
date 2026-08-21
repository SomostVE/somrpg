from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme


def _safe_return_url(request):
    referer = request.META.get("HTTP_REFERER", "")
    current = request.build_absolute_uri(request.get_full_path())
    if (
        referer
        and referer.rstrip("/") != current.rstrip("/")
        and url_has_allowed_host_and_scheme(
            referer,
            allowed_hosts={request.get_host()},
            require_https=request.is_secure(),
        )
    ):
        return referer
    return reverse("home")


def page_not_found(request, exception):
    messages.warning(
        request,
        "Page indisponible / Page unavailable. Cette fonction n'est peut-être pas encore prévue.",
    )
    return redirect(_safe_return_url(request))


def server_error(request):
    message = "Erreur inattendue / Unexpected error. L'action n'a pas pu être terminée."
    try:
        messages.error(request, message)
        target = _safe_return_url(request)
        if request.path != reverse("home") or target != reverse("home"):
            return redirect(target)
    except Exception:
        pass
    return HttpResponse(f"SomRPG — {message}", status=500, content_type="text/plain; charset=utf-8")
