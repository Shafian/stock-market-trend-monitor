from flask import Flask, render_template, request, jsonify, redirect, url_for
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


# ✅ Make last_symbol available globally (for navbar Analysis link)
@app.context_processor
def inject_last_symbol():
    return {
        "last_symbol": get_last_symbol()
    }


@app.route("/", methods=["GET"])
def index():
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


# 🔥 UPDATED — Redirect directly to analysis page
@app.route("/analyze", methods=["POST"])
def analyze():
    symbol = request.form.get("symbol", "").upper().strip()

    if not symbol:
        return redirect(url_for("index"))

    price = fetch_stock_price(symbol)
    if price is None:
        return redirect(url_for("index"))

    save_stock_price(symbol, price)

    # Immediately go to analysis page
    return redirect(url_for("analysis", symbol=symbol))


@app.route("/api/stock/<symbol>")
def api_stock(symbol):
    symbol = symbol.upper().strip()

    price = fetch_stock_price(symbol)
    if price is None:
        return jsonify({
            "error": "Could not fetch stock price",
            "symbol": symbol
        }), 400

    save_stock_price(symbol, price)
    avg_price = get_average_price(symbol)

    return jsonify({
        "symbol": symbol,
        "current_price": price,
        "average_price": avg_price
    })


@app.route("/history")
def history():
    history_data = get_history() or []
    return render_template("history.html", history=history_data)


@app.route("/analysis/<symbol>")
def analysis(symbol):
    symbol = symbol.upper()

    history_data = get_history() or []

    # All unique symbols for dropdown
    all_symbols = sorted(list({item["symbol"] for item in history_data}))

    # Filter selected symbol history
    symbol_history = [item for item in history_data if item["symbol"] == symbol]

    chart_data = symbol_history[:10]
    chart_data.reverse()

    prices = [item["price"] for item in chart_data]
    dates = [item["date"] for item in chart_data]

    # Summary metrics
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
    return render_template("about.html")


@app.route("/portfolio", methods=["GET", "POST"])
def portfolio():
    history_data = get_history() or []

    # All unique symbols from history
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
    app.run(debug=True)