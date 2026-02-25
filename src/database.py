import os
import sqlite3
import requests
import logging
import random

logging.basicConfig(level=logging.INFO)


def get_db_name():
    return os.getenv("DB_NAME", "stocks.db")


def get_conn():
    db_path = os.path.join(os.getcwd(), get_db_name())
    return sqlite3.connect(
        db_path,
        timeout=5,
        check_same_thread=False
    )


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


def generate_fallback_price(symbol):
    """
    Generates a consistent simulated price per symbol.
    This keeps your demo working even if API rate limits.
    """
    random.seed(symbol)
    base = random.uniform(100, 300)
    return round(base, 2)


def fetch_stock_price(symbol):
    api_key = os.getenv("ALPHA_VANTAGE_API_KEY")

    if not api_key:
        logging.warning("API KEY NOT FOUND — using fallback price.")
        return generate_fallback_price(symbol)

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

        logging.info(f"Alpha Vantage raw response: {data}")

        # Proper success case
        if (
            "Global Quote" in data and
            "05. price" in data["Global Quote"] and
            data["Global Quote"]["05. price"]
        ):
            return float(data["Global Quote"]["05. price"])

        # Rate limit or unexpected structure
        logging.warning(f"Invalid API response format for {symbol}. Using fallback.")
        return generate_fallback_price(symbol)

    except requests.RequestException as e:
        logging.error(f"Request failed: {e}. Using fallback.")
        return generate_fallback_price(symbol)

    except Exception as e:
        logging.error(f"Unexpected error: {e}. Using fallback.")
        return generate_fallback_price(symbol)


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