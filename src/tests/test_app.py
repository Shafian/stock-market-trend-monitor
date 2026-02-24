import pytest
from app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_homepage(client):
    response = client.get("/")
    assert response.status_code == 200


def test_history_page(client):
    response = client.get("/history")
    assert response.status_code == 200


def test_portfolio_page(client):
    response = client.get("/portfolio")
    assert response.status_code == 200