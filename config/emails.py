import logging

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

logger = logging.getLogger(__name__)


def get_from_email():
    """Gmail SMTP requires the From address to match the authenticated account."""
    from_email = settings.DEFAULT_FROM_EMAIL

    if (
        settings.EMAIL_HOST == "smtp.gmail.com"
        and settings.EMAIL_HOST_USER
        and settings.EMAIL_HOST_USER not in from_email
    ):
        return f"{settings.SITE_NAME} <{settings.EMAIL_HOST_USER}>"

    return from_email


def send_templated_email(subject, template_name, context, recipient_list, reply_to=None):
    if not recipient_list:
        return False

    recipient_list = [email for email in recipient_list if email]

    if not recipient_list:
        return False

    context = {
        "site_name": settings.SITE_NAME,
        "site_url": settings.SITE_URL,
        **context,
    }

    text_body = render_to_string(f"emails/{template_name}.txt", context)
    html_body = render_to_string(f"emails/{template_name}.html", context)

    message = EmailMultiAlternatives(
        subject=subject,
        body=text_body,
        from_email=get_from_email(),
        to=recipient_list,
        reply_to=[reply_to] if reply_to else None,
    )
    message.attach_alternative(html_body, "text/html")

    try:
        message.send(fail_silently=False)
        return True
    except Exception:
        logger.exception("Failed to send email '%s' to %s", subject, recipient_list)
        return False


def user_wants_order_updates(user):
    if not user.is_authenticated:
        return True

    profile = getattr(user, "profile", None)

    if profile is None:
        from accounts.models import UserProfile

        profile, _ = UserProfile.objects.get_or_create(user=user)

    return profile.receive_order_updates


def admin_recipients():
    if settings.ADMIN_ORDER_EMAIL:
        return [settings.ADMIN_ORDER_EMAIL]

    return [addr for _, addr in settings.ADMINS] if settings.ADMINS else []
