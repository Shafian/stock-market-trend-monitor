from flask import Flask, request
import random

app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return """
        <h1>Stock Market Trend Monitor</h1>
        <p>Enter a stock symbol to see a simple trend analysis.</p>

        <form action="/analyze" method="POST">
            <input name="symbol" placeholder="e.g. AAPL" required>
            <button type="submit">Analyze</button>
        </form>
    """

@app.route("/analyze", methods=["POST"])
def analyze():
    symbol = request.form.get("symbol", "").upper()

    trends = [
        "📈 Upward trend (bullish)",
        "📉 Downward trend (bearish)",
        "➖ Stable trend"
    ]

    trend_result = random.choice(trends)

    return f"""
        <h2>Analysis Result</h2>
        <p>You entered stock symbol: <strong>{symbol}</strong></p>
        <p>Trend: {trend_result}</p>
        <a href="/">Go back</a>
    """
