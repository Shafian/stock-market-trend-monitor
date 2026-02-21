from flask import Flask, render_template, request, jsonify
from database import (
    init_db,
    fetch_stock_price,
    save_stock_price,
    get_average_price,
    get_total_searches,
    get_last_symbol,
    get_history
)

app = Flask(__name__, template_folder="templates")

# Initialize database on startup
init_db()


@app.route("/", methods=["GET"])
def index():
    total_searches = get_total_searches()
    last_symbol = get_last_symbol()

    average_price = None
    if last_symbol:
        average_price = get_average_price(last_symbol)

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

    # Simple trend logic
    if avg_price and price > avg_price:
        direction = "UP"
    elif avg_price and price < avg_price:
        direction = "DOWN"
    else:
        direction = "STABLE"

    trend = f"📊 Current: ${price:.2f} | Average: ${avg_price:.2f} | Trend: {direction}"

    return render_template(
        "result.html",
        symbol=symbol,
        trend=trend
    )


@app.route("/history")
def history():
    history_data = get_history()
    return render_template("history.html", history=history_data)


# REST API endpoint (A-level rubric requirement)
@app.route("/api/stock/<symbol>", methods=["GET"])
def api_stock(symbol):
    symbol = symbol.upper()

    price = fetch_stock_price(symbol)

    if price is None:
        return jsonify({
            "symbol": symbol,
            "error": "Could not fetch stock price"
        }), 400

    avg_price = get_average_price(symbol)

    return jsonify({
        "symbol": symbol,
        "current_price": price,
        "average_price": avg_price
    })


if __name__ == "__main__":
    app.run(debug=True)
