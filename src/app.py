import os
import logging
from flask import Flask, render_template, request, jsonify, redirect, url_for
from src.database import (
    init_db,
    fetch_stock_price,
    save_stock_price,
    get_average_price,
    get_total_searches,
    get_last_symbol,
    get_history
)
from src.events import event_bus  


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)

logger = logging.getLogger(__name__)


app = Flask(__name__, template_folder="templates")

with app.app_context():
    logger.info("Initializing database...")
    init_db()
    logger.info("Database initialized successfully.")


def log_stock_event(data):
    logger.info(
        f"EVENT: Stock analyzed -> {data['symbol']} at {data['price']}"
    )

event_bus.subscribe("stock_analyzed", log_stock_event)


@app.route("/health")
def health():
    logger.info("Health check requested.")
    return {"status": "healthy"}, 200


@app.context_processor
def inject_last_symbol():
    return {
        "last_symbol": get_last_symbol()
    }


@app.route("/", methods=["GET"])
def index():
    logger.info("Homepage accessed.")

    total_searches = get_total_searches()
    last_symbol = get_last_symbol()

    average_price = None
    if last_symbol:
        average_price = get_average_price(last_symbol)

    history_data = get_history() or []
    latest_three = history_data[:3]

    return render_template(
        "index.html",
        total_searches=total_searches,
        last_symbol=last_symbol,
        average_price=average_price,
        latest_three=latest_three
    )

@app.route("/analyze", methods=["POST"])
def analyze():
    symbol = request.form.get("symbol", "").upper().strip()

    if not symbol:
        logger.warning("Analyze called with empty symbol.")
        return redirect(url_for("index"))

    logger.info(f"Analyze request received for symbol: {symbol}")

    try:
        price = fetch_stock_price(symbol)

        if price is None:
            logger.warning(f"Price fetch failed for symbol: {symbol}")
            return redirect(url_for("index"))

        save_stock_price(symbol, price)
        logger.info(f"Saved {symbol} price {price} to database.")

        # 🔥 Publish event
        event_bus.publish("stock_analyzed", {
            "symbol": symbol,
            "price": price
        })

    except Exception as e:
        logger.error(f"Error processing symbol {symbol}: {e}")
        return redirect(url_for("index"))

    return redirect(url_for("analysis", symbol=symbol))


@app.route("/api/stock/<symbol>")
def api_stock(symbol):
    symbol = symbol.upper().strip()
    logger.info(f"API request received for symbol: {symbol}")

    try:
        price = fetch_stock_price(symbol)

        if price is None:
            logger.warning(f"API price fetch failed for {symbol}")
            return jsonify({
                "error": "Could not fetch stock price",
                "symbol": symbol
            }), 400

        save_stock_price(symbol, price)
        avg_price = get_average_price(symbol)

        # 🔥 Publish event for API usage too
        event_bus.publish("stock_analyzed", {
            "symbol": symbol,
            "price": price
        })

        return jsonify({
            "symbol": symbol,
            "current_price": price,
            "average_price": avg_price
        })

    except Exception as e:
        logger.error(f"API error for {symbol}: {e}")
        return jsonify({"error": "Internal server error"}), 500


@app.route("/history")
def history():
    logger.info("History page accessed.")
    history_data = get_history() or []
    return render_template("history.html", history=history_data)


@app.route("/analysis/<symbol>")
def analysis(symbol):
    symbol = symbol.upper()
    logger.info(f"Analysis page accessed for symbol: {symbol}")

    history_data = get_history() or []

    all_symbols = sorted(list({item["symbol"] for item in history_data}))
    symbol_history = [item for item in history_data if item["symbol"] == symbol]

    chart_data = symbol_history[:10]
    chart_data.reverse()

    prices = [item["price"] for item in chart_data]
    dates = [item["date"] for item in chart_data]

    current_price = prices[-1] if prices else None
    previous_price = prices[-2] if len(prices) > 1 else None

    percent_change = 0
    trend = "STABLE"

    if current_price and previous_price:
        percent_change = ((current_price - previous_price) / previous_price) * 100
        if percent_change > 0:
            trend = "UP"
        elif percent_change < 0:
            trend = "DOWN"

    return render_template(
        "analysis.html",
        symbol=symbol,
        history=symbol_history,
        prices=prices,
        dates=dates,
        all_symbols=all_symbols,
        current_price=current_price,
        percent_change=percent_change,
        trend=trend
    )

@app.route("/about")
def about():
    logger.info("About page accessed.")
    return render_template("about.html")


@app.route("/portfolio", methods=["GET", "POST"])
def portfolio():
    logger.info("Portfolio page accessed.")

    history_data = get_history() or []
    all_symbols = sorted(list({item["symbol"] for item in history_data}))

    selected_symbol = None
    investment_amount = 10000
    prices = []
    dates = []
    portfolio_values = []
    profit_loss = 0
    percent_return = 0

    if request.method == "POST":
        selected_symbol = request.form.get("symbol")

        try:
            investment_amount = float(request.form.get("investment"))
        except:
            investment_amount = 10000

        symbol_history = [
            item for item in history_data
            if item["symbol"] == selected_symbol
        ]

        chart_data = symbol_history[:10]
        chart_data.reverse()

        prices = [item["price"] for item in chart_data]
        dates = [item["date"] for item in chart_data]

        if prices:
            shares = investment_amount / prices[0]
            portfolio_values = [round(shares * p, 2) for p in prices]

            final_value = portfolio_values[-1]
            profit_loss = round(final_value - investment_amount, 2)

            if investment_amount > 0:
                percent_return = round((profit_loss / investment_amount) * 100, 2)

        logger.info(
            f"Portfolio simulation for {selected_symbol} "
            f"Investment: {investment_amount} "
            f"Return: {percent_return}%"
        )

    return render_template(
        "portfolio.html",
        all_symbols=all_symbols,
        selected_symbol=selected_symbol,
        investment_amount=investment_amount,
        dates=dates,
        portfolio_values=portfolio_values,
        profit_loss=profit_loss,
        percent_return=percent_return
    )

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    logger.info(f"Starting application on port {port}")
    app.run(host="0.0.0.0", port=port)