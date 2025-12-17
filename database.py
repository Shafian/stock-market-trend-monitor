import sqlite3
import requests


def init_db():
    conn = sqlite3.connect("stocks.db")
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
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
    response = requests.get(url)
    data = response.json()

    try:
        price = data["chart"]["result"][0]["meta"]["regularMarketPrice"]
        return price
    except (KeyError, IndexError, TypeError):
        return None


def save_stock_price(symbol, price):
    conn = sqlite3.connect("stocks.db")
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO stock_data (symbol, price) VALUES (?, ?)",
        (symbol.upper(), price)
    )

    conn.commit()
    conn.close()


if __name__ == "__main__":
    init_db()
