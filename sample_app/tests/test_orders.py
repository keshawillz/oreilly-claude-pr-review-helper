import json
from pathlib import Path

import pytest

from app import db, orders

FIXTURES = Path(__file__).parent / "fixtures"


def load_orders():
    return json.loads((FIXTURES / "orders.json").read_text())


def test_order_total_without_a_code():
    order = load_orders()[0]
    assert orders.order_total(order["items"]) == 21.6


def test_order_total_with_a_code():
    order = load_orders()[1]
    assert orders.order_total(order["items"], order["code"]) == 86.4


def test_create_order_and_read_status():
    conn = db.connect()
    order = load_orders()[0]
    order_id = orders.create_order(conn, order["user_id"], order["items"])
    assert orders.get_order_status(conn, order_id) == "new"


def test_missing_order_raises():
    conn = db.connect()
    with pytest.raises(orders.OrderNotFound):
        orders.get_order_status(conn, 999)
