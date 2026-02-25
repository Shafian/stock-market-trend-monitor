import os
import sqlite3
import requests
import logging

API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")

logging.basicConfig(level=logging.INFO)


def get_db_name():
    # Read at runtime so tests can override via env var
    return os.getenv("DB_NAME", "stocks.db")


def get_conn():
    return sqlite3.connect(get_db_name())


def init_db():
    conn = get_conn()
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
    api_key = os.getenv("ALPHA_VANTAGE_API_KEY")  # runtime read

    if not api_key:
        logging.error("API KEY NOT FOUND")
        return None

    logging.info(f"Fetching stock price for {symbol}")

    url = "https://www.alphavantage.co/query"
    params = {
        "function": "GLOBAL_QUOTE",
        "symbol": symbol,
        "apikey": api_key
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        logging.info(f"Alpha Vantage response received for {symbol}")

        return float(data["Global Quote"]["05. price"])

    except (KeyError, TypeError, ValueError):
        logging.warning(f"Invalid response format for {symbol}")
        return None
    except requests.RequestException as e:
        logging.error(f"Request failed: {e}")
        return None


def save_stock_price(symbol, price):
    conn = get_conn()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO stock_data (symbol, price) VALUES (?, ?)",
        (symbol, price)
    )

    conn.commit()
    conn.close()


def get_average_price(symbol):
    conn = get_conn()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT AVG(price) FROM stock_data WHERE symbol = ?",
        (symbol,)
    )

    result = cursor.fetchone()
    conn.close()

    if result and result[0] is not None:
        return round(result[0], 2)

    return None


def get_total_searches():
    conn = get_conn()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM stock_data")
    count = cursor.fetchone()[0]

    conn.close()
    return count


def get_last_symbol():
    conn = get_conn()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT symbol FROM stock_data ORDER BY timestamp DESC LIMIT 1"
    )
    result = cursor.fetchone()

    conn.close()

    if result:
        return result[0]
    return None


def clear_all_data():
    """Helpful for tests: wipes table completely."""
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM stock_data")
    conn.commit()
    conn.close()


def get_history():
    conn = get_conn()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT symbol, price, timestamp
        FROM stock_data
        ORDER BY symbol, timestamp ASC
    """)

    rows = cursor.fetchall()
    conn.close()

    history = []
    previous_prices = {}

    for symbol, price, timestamp in rows:
        trend = "STABLE"
        percent_change = 0.0

        if symbol in previous_prices:
            old_price = previous_prices[symbol]

            if price > old_price:
                trend = "UP"
            elif price < old_price:
                trend = "DOWN"

            if old_price != 0:
                percent_change = ((price - old_price) / old_price) * 100

        previous_prices[symbol] = price

        history.append({
            "symbol": symbol,
            "price": price,
            "date": timestamp,
            "trend": trend,
            "percent_change": percent_change
        })

    history.reverse()
    return history