SESSION_CART_KEY = "cart"
SESSION_COUPON_KEY = "coupon_code"


def _get_raw_cart(session):
    cart = session.get(SESSION_CART_KEY, [])

    if not isinstance(cart, list):
        return []

    return cart


def _line_key(product_id, variant_id):
    variant_part = variant_id or 0
    return f"{product_id}:{variant_part}"


def _find_line_index(cart, product_id, variant_id=None):
    key = _line_key(product_id, variant_id)

    for index, line in enumerate(cart):
        if _line_key(line.get("product_id"), line.get("variant_id")) == key:
            return index

    return None


def get_session_cart(session):
    return _get_raw_cart(session)


def add_to_session_cart(session, product_id, variant_id=None, quantity=1):
    cart = _get_raw_cart(session)
    index = _find_line_index(cart, product_id, variant_id)

    if index is None:
        cart.append(
            {
                "product_id": product_id,
                "variant_id": variant_id,
                "quantity": quantity,
            }
        )
    else:
        cart[index]["quantity"] += quantity

    session[SESSION_CART_KEY] = cart
    session.modified = True


def set_session_cart_quantity(session, product_id, variant_id, quantity):
    cart = _get_raw_cart(session)
    index = _find_line_index(cart, product_id, variant_id)

    if index is None:
        return

    if quantity <= 0:
        cart.pop(index)
    else:
        cart[index]["quantity"] = quantity

    session[SESSION_CART_KEY] = cart
    session.modified = True


def remove_from_session_cart(session, product_id, variant_id=None):
    cart = _get_raw_cart(session)
    index = _find_line_index(cart, product_id, variant_id)

    if index is not None:
        cart.pop(index)

    session[SESSION_CART_KEY] = cart
    session.modified = True


def clear_session_cart(session):
    session.pop(SESSION_CART_KEY, None)
    session.modified = True


def get_session_cart_count(session):
    return sum(line.get("quantity", 0) for line in _get_raw_cart(session))


def get_session_coupon_code(session):
    return session.get(SESSION_COUPON_KEY, "")


def set_session_coupon_code(session, code):
    if code:
        session[SESSION_COUPON_KEY] = code.upper().strip()
    else:
        session.pop(SESSION_COUPON_KEY, None)
    session.modified = True
