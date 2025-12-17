from flask import Flask, render_template, request
from .database import init_db, fetch_stock_price, save_stock_price

app = Flask(__name__, template_folder="templates")

# Initialize database on startup
init_db()


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/analyze", methods=["POST"])
def analyze():
    symbol = request.form.get("symbol", "").upper().strip()

    if not symbol:
        return render_template(
            "result.html",
            symbol="",
            trend="No stock symbol entered"
        )

    # Fetch price from Yahoo Finance API
    price = fetch_stock_price(symbol)

    # Handle API failure or invalid symbol
    if price is None:
        return render_template(
            "result.html",
            symbol=symbol,
            trend="Could not fetch stock price (invalid symbol or API error)"
        )

    # Save to database
    save_stock_price(symbol, price)

    # Simple trend logic (placeholder)
    trend = "📈 Upward trend (bullish)"

    return render_template(
        "result.html",
        symbol=symbol,
        trend=trend
    )


if __name__ == "__main__":
    app.run(debug=True)
