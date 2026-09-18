"""Prices, discounts, and tax."""

TAX_RATE = 0.08
DISCOUNT_CODES = {"WELCOME10": 0.10, "VIP20": 0.20}


def apply_discount(total, rate):
    """Return total after a discount.

    rate is a fraction between 0 and 1. Pass 0.2 for 20 percent.
    """
    if rate < 0 or rate > 1:
        raise ValueError("rate must be between 0 and 1")
    return round(total * (1 - rate), 2)


def add_tax(total):
    return round(total * (1 + TAX_RATE), 2)


def average_item_price(items):
    if not items:
        return 0.0
    total = 0.0
    for item in items:
        total += item["price"]
    return round(total / len(items), 2)
