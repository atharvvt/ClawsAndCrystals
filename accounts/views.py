from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import redirect, render
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect

from cart.utils import merge_session_cart_into_user

from .forms import RegisterForm


def _redirect_after_auth(request):
    next_url = request.GET.get("next") or request.POST.get("next")
    if next_url:
        return redirect(next_url)
    return redirect("home")


@never_cache
@csrf_protect
def register_view(request):

    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":

        form = RegisterForm(request.POST)

        if form.is_valid():

            user = form.save()

            login(request, user)
            merge_session_cart_into_user(request)
            messages.success(request, "Welcome! Your cart has been saved.")
            return _redirect_after_auth(request)

    else:
        form = RegisterForm()

    return render(
        request,
        "accounts/register.html",
        {
            "form": form
        }
    )


@never_cache
@csrf_protect
def login_view(request):

    if request.user.is_authenticated:
        return redirect("home")

    form = AuthenticationForm(request, data=request.POST or None)

    if request.method == "POST" and form.is_valid():
        login(request, form.get_user())
        merge_session_cart_into_user(request)
        return _redirect_after_auth(request)

    return render(
        request,
        "accounts/login.html",
        {
            "form": form,
            "error": "Invalid username or password" if request.method == "POST" else None,
            "next": request.GET.get("next", ""),
        }
    )


def logout_view(request):

    from django.contrib.auth import logout

    logout(request)

    return redirect("home")
