import os
import sqlite3
import requests
import logging

# Environment configuration (A-level requirement)
API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")
DB_NAME = os.getenv("DB_NAME", "stocks.db")

# Production logging (monitoring requirement)
logging.basicConfig(level=logging.INFO)


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
        logging.error("API KEY NOT FOUND")
        return None

    logging.info(f"Fetching stock price for {symbol}")

    url = "https://www.alphavantage.co/query"
    params = {
        "function": "GLOBAL_QUOTE",
        "symbol": symbol,
        "apikey": API_KEY 
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        print(data)
        logging.info(f"Alpha Vantage response received for {symbol}")

        return float(data["Global Quote"]["05. price"])

    except (KeyError, TypeError, ValueError):
        logging.warning(f"Invalid response format for {symbol}")
        return None
    except requests.RequestException as e:
        logging.error(f"Request failed: {e}")
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


def get_average_price(symbol):
    conn = sqlite3.connect(DB_NAME)
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
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM stock_data")
    count = cursor.fetchone()[0]

    conn.close()
    return count


def get_last_symbol():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT symbol FROM stock_data ORDER BY timestamp DESC LIMIT 1"
    )
    result = cursor.fetchone()

    conn.close()

    if result:
        return result[0]
    return None


# Reporting feature for history page
def get_history():
    conn = sqlite3.connect(DB_NAME)
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

            # Calculate percent change
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