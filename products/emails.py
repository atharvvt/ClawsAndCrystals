from config.emails import admin_recipients, send_templated_email


def send_low_stock_alert(product):
    recipients = admin_recipients()

    if not recipients:
        return False

    return send_templated_email(
        subject=f"Low stock: {product.name} ({product.stock} left)",
        template_name="low_stock_alert",
        context={"product": product},
        recipient_list=recipients,
    )
