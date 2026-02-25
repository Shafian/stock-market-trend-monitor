import pytest
from unittest.mock import patch
from app import app
from database import get_history


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


# -------------------------------------------------
# 1️⃣ REAL INTEGRATION TEST (Route → DB → Read Back)
# -------------------------------------------------
@patch("app.fetch_stock_price")
def test_analyze_saves_to_db(mock_fetch, client):
    mock_fetch.return_value = 150.0

    response = client.post(
        "/analyze",
        data={"symbol": "AAPL"},
        follow_redirects=True
    )

    assert response.status_code == 200

    history = get_history()
    assert len(history) == 1
    assert history[0]["symbol"] == "AAPL"
    assert float(history[0]["price"]) == 150.0


# -------------------------------------------------
# 2️⃣ SPY TEST (Verify Interactions)
# -------------------------------------------------
@patch("app.save_stock_price")
@patch("app.fetch_stock_price")
def test_analyze_calls_dependencies(mock_fetch, mock_save, client):
    mock_fetch.return_value = 123.45

    response = client.post(
        "/analyze",
        data={"symbol": "MSFT"},
        follow_redirects=True
    )

    assert response.status_code == 200

    # Spy behavior: verify calls
    mock_fetch.assert_called_once_with("MSFT")
    mock_save.assert_called_once_with("MSFT", 123.45)


# -------------------------------------------------
# 3️⃣ FAKE SERVICE TEST (Using monkeypatch)
# -------------------------------------------------
def fake_stock_service(symbol):
    fake_prices = {
        "AAPL": 150.0,
        "TSLA": 200.0,
        "MSFT": 300.0
    }
    return fake_prices.get(symbol, 100.0)


def test_with_fake_service(monkeypatch, client):
    monkeypatch.setattr("app.fetch_stock_price", fake_stock_service)

    response = client.post(
        "/analyze",
        data={"symbol": "TSLA"},
        follow_redirects=True
    )

    assert response.status_code == 200

    history = get_history()
    assert history[0]["symbol"] == "TSLA"
    assert float(history[0]["price"]) == 200.0