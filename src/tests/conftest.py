import os
import pytest
from database import init_db


@pytest.fixture(autouse=True)
def setup_test_db(tmp_path, monkeypatch):
    # Create a fresh temp DB for each test session
    test_db = tmp_path / "test_stocks.db"
    monkeypatch.setenv("DB_NAME", str(test_db))
    monkeypatch.setenv("ALPHA_VANTAGE_API_KEY", "TEST_KEY")

    # IMPORTANT: initialize DB AFTER setting env var
    init_db()

    yield