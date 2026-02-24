import os
import pytest
from unittest.mock import patch
from app import app
from database import init_db, get_history


@pytest.fixture
def client(tmp_path):
    test_db = tmp_path / "test.db"
    os.environ["DB_NAME"] = str(test_db)

    init_db()

    app.config["TESTING"] = True

    with app.test_client() as client:
        yield client

    os.environ.pop("DB_NAME", None)


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
    assert history[0]["price"] == 150.0


@patch("app.fetch_stock_price")
def test_history_shows_saved_symbol(mock_fetch, client):
    mock_fetch.return_value = 200.0

    client.post("/analyze", data={"symbol": "TSLA"})

    response = client.get("/history")

    assert response.status_code == 200
    assert b"TSLA" in response.data