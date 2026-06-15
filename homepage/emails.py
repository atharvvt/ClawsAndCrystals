from django.conf import settings

from config.emails import admin_recipients, send_templated_email


def send_contact_notification(suggestion):
    recipients = admin_recipients()

    if not recipients:
        return False

    return send_templated_email(
        subject=f"Contact: {suggestion.subject}",
        template_name="contact_notification",
        context={"suggestion": suggestion},
        recipient_list=recipients,
        reply_to=suggestion.email,
    )
