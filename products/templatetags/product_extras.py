from django import template
from django.utils.html import escape
from django.utils.safestring import mark_safe
import re

register = template.Library()


@register.filter
def highlight_search(text, query):
    if not query or not text:
        return text

    pattern = re.compile(re.escape(query), re.IGNORECASE)

    def replacer(match):
        return f'<mark class="search-highlight">{escape(match.group(0))}</mark>'

    return mark_safe(pattern.sub(replacer, escape(str(text))))


@register.simple_tag
def product_image_url(image_field, alias="product_card"):
    if not image_field:
        return ""

    try:
        from easy_thumbnails.files import get_thumbnailer

        thumbnailer = get_thumbnailer(image_field)
        thumb = thumbnailer.get_thumbnail({"size": _alias_size(alias), "crop": True})
        return thumb.url
    except Exception:
        return image_field.url


def _alias_size(alias):
    sizes = {
        "product_card": (400, 400),
        "product_gallery": (800, 800),
        "product_thumb": (120, 120),
    }
    return sizes.get(alias, (400, 400))
