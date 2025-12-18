from flask import Flask, render_template, request
from src.database import init_db, fetch_stock_price, save_stock_price

app = Flask(__name__, template_folder="templates")

# Initialize database
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

    price = fetch_stock_price(symbol)

    if price is None:
        return render_template(
            "result.html",
            symbol=symbol,
            trend="Could not fetch stock price (API error or invalid symbol)"
        )

    save_stock_price(symbol, price)

    trend = f"📈 Current price: ${price}"

    return render_template(
        "result.html",
        symbol=symbol,
        trend=trend
    )


if __name__ == "__main__":
    app.run()
