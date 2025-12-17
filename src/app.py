from flask import Flask, request

app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return """
        <h1>Stock Market Trend Monitor</h1>
        <p>Enter a stock symbol to see a simple trend message.</p>

        <form action="/analyze" method="POST">
            <input name="symbol" placeholder="e.g. AAPL" required>
            <button type="submit">Analyze</button>
        </form>
    """

@app.route("/analyze", methods=["POST"])
def analyze():
    symbol = request.form.get("symbol", "").upper()
    return f"""
        <h2>Analysis Result</h2>
        <p>You entered stock symbol: <strong>{symbol}</strong></p>
        <p>Trend: Data analysis coming soon 📈</p>
        <a href="/">Go back</a>
    """
