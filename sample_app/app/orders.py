"""Create and read orders."""
from app import db, pricing


class OrderNotFound(Exception):
    pass


def order_total(items, code=None):
    subtotal = 0.0
    for item in items:
        subtotal += item["price"] * item["quantity"]
    if code in pricing.DISCOUNT_CODES:
        subtotal = pricing.apply_discount(subtotal, pricing.DISCOUNT_CODES[code])
    return pricing.add_tax(subtotal)


def create_order(conn, user_id, items, code=None):
    if not items:
        raise ValueError("an order needs at least one item")
    total = order_total(items, code)
    return db.insert_order(conn, user_id, total)


def get_order_status(conn, order_id):
    order = db.find_order(conn, order_id)
    if order is None:
        raise OrderNotFound(f"order {order_id} does not exist")
    return order["status"]
