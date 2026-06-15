from decimal import Decimal

from .models import ShippingSettings, ShippingZone


def resolve_shipping_rules(state="", pincode=""):
    settings = ShippingSettings.get_active()
    flat_rate = settings.flat_rate
    free_shipping_threshold = settings.free_shipping_threshold
    zone_name = "Standard"

    for zone in ShippingZone.objects.filter(is_active=True):
        if zone.matches(state=state, pincode=pincode):
            if zone.flat_rate is not None:
                flat_rate = zone.flat_rate
            if zone.free_shipping_threshold is not None:
                free_shipping_threshold = zone.free_shipping_threshold
            zone_name = zone.name
            break

    return {
        "flat_rate": flat_rate,
        "free_shipping_threshold": free_shipping_threshold,
        "zone_name": zone_name,
    }


def calculate_shipping_amount(subtotal, *, state="", pincode="", force_free=False):
    rules = resolve_shipping_rules(state=state, pincode=pincode)

    if force_free or subtotal >= rules["free_shipping_threshold"]:
        return Decimal("0.00"), f"Free shipping ({rules['zone_name']})"

    return rules["flat_rate"], f"Standard delivery ({rules['zone_name']})"
