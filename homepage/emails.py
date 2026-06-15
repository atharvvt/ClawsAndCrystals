import logging

from django.conf import settings

from config.emails import admin_recipients, send_templated_email

logger = logging.getLogger(__name__)


def send_contact_notification(suggestion):
    recipients = admin_recipients()

    if not recipients:
        logger.warning(
            "Contact form submission saved (id=%s) but no admin recipients configured. "
            "Set ADMIN_ORDER_EMAIL in .env.",
            suggestion.id,
        )
        return False

    sent = send_templated_email(
        subject=f"Contact: {suggestion.subject}",
        template_name="contact_notification",
        context={"suggestion": suggestion},
        recipient_list=recipients,
        reply_to=suggestion.email,
    )

    if not sent:
        logger.error(
            "Failed to send contact notification for suggestion id=%s to %s",
            suggestion.id,
            recipients,
        )

    return sent
