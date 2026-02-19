from flask import Flask, render_template, request
from database import init_db, fetch_stock_price, save_stock_price, get_average_price

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
            trend="No stock symbol entered",
            average=None
        )

    price = fetch_stock_price(symbol)

    if price is None:
        return render_template(
            "result.html",
            symbol=symbol,
            trend="Could not fetch stock price (API error or invalid symbol)",
            average=None
        )

    # Save price to database
    save_stock_price(symbol, price)

    # Get average price from database
    average_price = get_average_price(symbol)

    trend = f"📈 Current price: ${price}"

    return render_template(
        "result.html",
        symbol=symbol,
        trend=trend,
        average=average_price
    )


if __name__ == "__main__":
    app.run()
