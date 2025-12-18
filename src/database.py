import os
import sqlite3
import requests

API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")
DB_NAME = "stocks.db"


def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS stock_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT,
            price REAL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


def fetch_stock_price(symbol):
    if not API_KEY:
        print("API KEY NOT FOUND")
        return None

    url = "https://www.alphavantage.co/query"
    params = {
        "function": "GLOBAL_QUOTE",
        "symbol": symbol,
        "apikey": API_KEY
    }

    response = requests.get(url, params=params)
    data = response.json()

    print("Alpha Vantage response:", data)  # DEBUG

    try:
        return float(data["Global Quote"]["05. price"])
    except (KeyError, TypeError, ValueError):
        return None


def save_stock_price(symbol, price):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO stock_data (symbol, price) VALUES (?, ?)",
        (symbol, price)
    )

    conn.commit()
    conn.close()
