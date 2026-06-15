from django.contrib import messages
from django.shortcuts import redirect


def csrf_failure(request, reason=""):
    messages.error(
        request,
        "Your session expired or the page was open too long. Please try again.",
    )

    if request.path.startswith("/accounts/login"):
        return redirect("login")

    if request.path.startswith("/accounts/register"):
        return redirect("register")

    next_url = request.META.get("HTTP_REFERER")
    if next_url:
        return redirect(next_url)

    return redirect("login")
