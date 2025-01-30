from flask import Flask, jsonify, render_template_string
import yfinance as yf
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# List of Bank Nifty stock symbols
bank_nifty_symbols = [
    "HDFCBANK.NS", "ICICIBANK.NS", "SBIN.NS", "KOTAKBANK.NS", "AXISBANK.NS", 
    "BANKBARODA.NS", "PNB.NS", "CANBK.NS", "INDUSINDBK.NS", "FEDERALBNK.NS",  "AUBANK.NS",
    "IDFCFIRSTB.NS" , 
]

# Fetch stock data
@app.route('/api/banknifty', methods=['GET'])
def get_banknifty_data():
    data = []
    errors = []

    for symbol in bank_nifty_symbols:
        try:
            stock = yf.Ticker(symbol)
            # Fetch the last 5 days of data
            stock_data = stock.history(period="5d")  
            
            if not stock_data.empty and len(stock_data) > 1:
                # Get the latest and previous day's data
                latest = stock_data.iloc[-1]
                previous = stock_data.iloc[-2]  # The previous day's close

                price = latest["Close"]
                prev_close = previous["Close"]  # Previous day's close price
                percent_change = ((price - prev_close) / prev_close) * 100  # Calculate percentage change

                data.append({
                    "symbol": symbol,
                    "price": price,
                    "percent_change": percent_change,
                    "open_price": latest["Open"]
                })
            else:
                errors.append(f"No sufficient data found for {symbol}")
        except Exception as e:
            errors.append(f"Error for {symbol}: {e}")

    return jsonify({"data": data, "errors": errors})

# Serve HTML
@app.route('/')
def index():
    html = """
    <!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Bank Nifty Stock Analysis</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #f9f9f9;
            color: #333;
        }
        h1 {
            text-align: center;
            background-color: #4CAF50;
            color: white;
            padding: 10px 0;
            margin: 0;
        }
        .stock-container {
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            margin-top: 20px;
        }
        .stock-box {
            width: 200px;
            margin: 10px;
            padding: 20px;
            text-align: center;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            transition: background-color 0.3s ease;
        }
        .symbol {
            font-size: 20px;
            font-weight: bold;
        }
        .price {
            font-size: 18px;
            font-weight: bold;
            margin: 10px 0;
        }
        .percent-change {
            font-size: 16px;
        }
        .price-change {
            font-size: 16px;
            margin-top: 10px;
        }
        .summary {
            text-align: center;
            margin-top: 20px;
            font-size: 18px;
        }
    </style>
</head>
<body>
    <h1>Bank Nifty Stock Analysis</h1>
    <div class="stock-container" id="stock-container">
        <!-- Stock boxes will be inserted here -->
    </div>

    <div class="summary" id="summary">
        <!-- Summary will be inserted here -->
    </div>

    <script>
        function getBoxColor(percentChange) {
            let red, green;

            if (percentChange > 0) {
                // Positive: Exact Green #008000
                red = 0;
                green = 128; // Green component for #008000
            } else {
                // Negative: Red (darker red for larger negative change)
                red = Math.min(255, 200 + Math.abs(percentChange) * 6);  // Darker red for negative change
                green = Math.max(0, 255 - red);  // Decrease green as red increases
            }

            return `rgb(${red}, ${green}, 0)`;  // No blue component, only red and green
        }

        async function fetchStockData() {
            try {
                const response = await fetch('/api/banknifty');
                const { data } = await response.json();

                const container = document.getElementById('stock-container');
                container.innerHTML = '';  // Clear the container before appending new data

                let positiveCount = 0;
                let negativeCount = 0;
                let positiveTotalPercent = 0;
                let negativeTotalPercent = 0;
                let totalPercent = 0; // Total percentage change for all stocks

                // Loop through each stock and display its details
                data.forEach(stock => {
                    const stockBox = document.createElement('div');
                    stockBox.classList.add('stock-box');
                    
                    // Set background color based on percent change
                    const color = getBoxColor(stock.percent_change);
                    stockBox.style.backgroundColor = color;

                    // Ensure open_price is defined and calculate price change in rupees
                    const priceChange = stock.price && stock.open_price ? (stock.price - stock.open_price).toFixed(2) : 0;
                    const priceChangeText = priceChange !== "0" ? `₹${priceChange} ${priceChange > 0 ? '↑' : '↓'}` : '';

                    stockBox.innerHTML = `
                        <div class="symbol">${stock.symbol}</div>
                        <div class="price">${stock.price.toFixed(2)}</div>
                        <div class="percent-change">${stock.percent_change.toFixed(2)}%</div>
                    `;
                    
                    container.appendChild(stockBox);

                    // Count positive and negative stocks and calculate total percentage
                    if (stock.percent_change >= 0) {
                        positiveCount++;
                        positiveTotalPercent += stock.percent_change;
                    } else {
                        negativeCount++;
                        negativeTotalPercent += stock.percent_change;
                    }

                    // Calculate the overall percentage change for all stocks
                    totalPercent += stock.percent_change;
                });

                // Display the summary (positive/negative count, total percentage)
                const summaryEl = document.getElementById('summary');
                summaryEl.innerHTML = `
                    <p>Positive Stocks: ${positiveCount} | Total Positive %: ${positiveTotalPercent.toFixed(2)}%</p>
                    <p>Negative Stocks: ${negativeCount} | Total Negative %: ${negativeTotalPercent.toFixed(2)}%</p>
                    <p>Total Overall % Change: ${totalPercent.toFixed(2)}%</p>
                `;
            } catch (err) {
                console.error("Error fetching stock data:", err);
                document.getElementById('errors').textContent = `Error fetching data: ${err.message}`;
            }
        }

        fetchStockData();
        setInterval(fetchStockData, 100);  // Refresh every 10 seconds
    </script>
</body>
</html>
    """
    return render_template_string(html)

if __name__ == '__main__':
    app.run(debug=True)
