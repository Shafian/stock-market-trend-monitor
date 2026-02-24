import pytest


def calculate_portfolio(prices, investment):
    shares = investment / prices[0]
    return [round(shares * p, 2) for p in prices]


def test_portfolio_growth():
    prices = [100, 110, 120]
    investment = 1000

    values = calculate_portfolio(prices, investment)

    assert values[0] == 1000.00
    assert values[1] == 1100.00
    assert values[2] == 1200.00


def test_portfolio_no_change():
    prices = [100, 100, 100]
    investment = 1000

    values = calculate_portfolio(prices, investment)

    assert all(v == 1000 for v in values)