from django.urls import path

from .password_reset_views import (
    PasswordResetCompleteView,
    PasswordResetConfirmView,
    PasswordResetDoneView,
    PasswordResetView,
)
from .profile_views import (
    profile_address_add,
    profile_address_delete,
    profile_address_edit,
    profile_address_set_default,
    profile_addresses,
    profile_dashboard,
    profile_edit,
    profile_password,
    profile_settings,
)
from .views import login_view, logout_view, register_view

urlpatterns = [
    path("register/", register_view, name="register"),
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path(
        "password-reset/",
        PasswordResetView.as_view(),
        name="password_reset",
    ),
    path(
        "password-reset/done/",
        PasswordResetDoneView.as_view(),
        name="password_reset_done",
    ),
    path(
        "password-reset/<uidb64>/<token>/",
        PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path(
        "password-reset/complete/",
        PasswordResetCompleteView.as_view(),
        name="password_reset_complete",
    ),
    path("profile/", profile_dashboard, name="profile"),
    path("profile/edit/", profile_edit, name="profile_edit"),
    path("profile/settings/", profile_settings, name="profile_settings"),
    path("profile/password/", profile_password, name="profile_password"),
    path("profile/addresses/", profile_addresses, name="profile_addresses"),
    path("profile/addresses/add/", profile_address_add, name="profile_address_add"),
    path(
        "profile/addresses/<int:address_id>/edit/",
        profile_address_edit,
        name="profile_address_edit",
    ),
    path(
        "profile/addresses/<int:address_id>/delete/",
        profile_address_delete,
        name="profile_address_delete",
    ),
    path(
        "profile/addresses/<int:address_id>/default/",
        profile_address_set_default,
        name="profile_address_set_default",
    ),
]
