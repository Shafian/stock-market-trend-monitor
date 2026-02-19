from flask import Flask, render_template, request
from .database import (
    init_db,
    fetch_stock_price,
    save_stock_price,
    get_average_price,
    get_total_searches,
    get_last_searched_symbol
)

app = Flask(__name__, template_folder="templates")

# Initialize database on startup
init_db()


@app.route("/", methods=["GET"])
def index():
    total_searches = get_total_searches()
    last_symbol = get_last_searched_symbol()

    average_price = None
    if last_symbol:
        avg = get_average_price(last_symbol)
        if avg:
            average_price = f"${avg:.2f}"

    return render_template(
        "index.html",
        total_searches=total_searches,
        last_symbol=last_symbol,
        average_price=average_price
    )


@app.route("/analyze", methods=["POST"])
def analyze():
    symbol = request.form.get("symbol", "").upper().strip()

    if not symbol:
        return render_template(
            "result.html",
            symbol="",
            trend="No stock symbol entered"
        )

    price = fetch_stock_price(symbol)

    if price is None:
        return render_template(
            "result.html",
            symbol=symbol,
            trend="Could not fetch stock price (API error or invalid symbol)"
        )

    save_stock_price(symbol, price)

    avg_price = get_average_price(symbol)

    trend = f"📈 Current price: ${price} | Average price: ${avg_price:.2f}"

    return render_template(
        "result.html",
        symbol=symbol,
        trend=trend
    )
