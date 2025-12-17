from flask import Flask, request, render_template_string
from database import init_db, fetch_stock_price, save_stock_price

app = Flask(__name__)
init_db()

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        symbol = request.form["symbol"]
        price = fetch_stock_price(symbol)

        if price is not None:
            save_stock_price(symbol, price)
            trend = "Upward trend (bullish) 📈"
        else:
            trend = "Data unavailable ❌"

        return f"""
        <h1>Analysis Result</h1>
        <p>You entered stock symbol: <b>{symbol.upper()}</b></p>
        <p>Current Price: ${price}</p>
        <p>Trend: {trend}</p>
        <a href="/">Go back</a>
        """

    return """
    <h1>Stock Market Trend Monitor</h1>
    <form method="post">
        <input name="symbol" placeholder="Enter stock symbol (AAPL)">
        <button type="submit">Analyze</button>
    </form>
    """

if __name__ == "__main__":
    app.run()
