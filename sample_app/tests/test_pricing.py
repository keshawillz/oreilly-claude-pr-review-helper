import pytest

from app import pricing


def test_apply_discount_takes_a_fraction():
    assert pricing.apply_discount(100.0, 0.2) == 80.0


def test_apply_discount_rejects_a_percent():
    with pytest.raises(ValueError):
        pricing.apply_discount(100.0, 20)


def test_add_tax():
    assert pricing.add_tax(100.0) == 108.0


def test_average_item_price():
    assert pricing.average_item_price([{"price": 10.0}, {"price": 20.0}]) == 15.0
