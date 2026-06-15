from dataclasses import dataclass


@dataclass
class SessionCartLine:
    product: object
    variant: object
    quantity: int
    session_key: str

    @property
    def id(self):
        return self.session_key

    @property
    def total_price(self):
        from orders.pricing import get_line_total

        return get_line_total(self)

    @property
    def is_session_line(self):
        return True
