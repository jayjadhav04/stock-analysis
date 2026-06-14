from flask import Flask, jsonify, render_template_string
import yfinance as yf
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# --- Lists of Stock Symbols ---
bank_nifty_symbols = [
    "HDFCBANK.NS", "ICICIBANK.NS", "SBIN.NS", "KOTAKBANK.NS", "AXISBANK.NS", 
    "BANKBARODA.NS", "PNB.NS", "CANBK.NS", "INDUSINDBK.NS", "FEDERALBNK.NS", "AUBANK.NS", "IDFCFIRSTB.NS"
]

nifty50_symbols = [
    "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "BHARTIARTL.NS", "ICICIBANK.NS", "INFY.NS", "SBIN.NS", "ITC.NS", "HINDUNILVR.NS", "LT.NS", "HCLTECH.NS", "SUNPHARMA.NS", "BAJFINANCE.NS", "M&M.NS", "NTPC.NS", "KOTAKBANK.NS", "AXISBANK.NS", "MARUTI.NS", "ULTRACEMCO.NS", "ONGC.NS", "WIPRO.NS", "TITAN.NS", "POWERGRID.NS", "TATAMOTORS.NS", "ADANIENT.NS", "ADANIPORTS.NS", "BAJAJFINSV.NS", "COALINDIA.NS", "BAJAJ-AUTO.NS", "JSWSTEEL.NS", "TRENT.NS", "BEL.NS", "ASIANPAINT.NS", "NESTLEIND.NS", "TATASTEEL.NS", "GRASIM.NS", "TECHM.NS", "HINDALCO.NS", "SBILIFE.NS", "HDFCLIFE.NS", "EICHERMOT.NS", "BPCL.NS", "SHRIRAMFIN.NS", "CIPLA.NS", "BRITANNIA.NS", "APOLLOHOSP.NS", "DRREDDY.NS", "HEROMOTOCO.NS", "TATACONSUM.NS", "INDUSINDBK.NS"
]

# --- Helper Function to Fetch Data ---
def fetch_stock_data(symbols):
    data = []
    errors = []
    for symbol in symbols:
        try:
            stock = yf.Ticker(symbol)
            stock_data = stock.history(period="5d")  
            
            if not stock_data.empty and len(stock_data) > 1:
                latest = stock_data.iloc[-1]
                previous = stock_data.iloc[-2]

                price = latest["Close"]
                prev_close = previous["Close"]
                percent_change = ((price - prev_close) / prev_close) * 100

                data.append({
                    "symbol": symbol,
                    "price": price,
                    "percent_change": percent_change,
                    "open_price": latest["Open"]
                })
            else:
                errors.append(f"No data for {symbol}")
        except Exception as e:
            errors.append(f"Error for {symbol}: {e}")
    return {"data": data, "errors": errors}

# --- API Routes ---
@app.route('/api/banknifty', methods=['GET'])
def get_banknifty_data():
    return jsonify(fetch_stock_data(bank_nifty_symbols))

@app.route('/api/nifty50', methods=['GET'])
def get_nifty50_data():
    return jsonify(fetch_stock_data(nifty50_symbols))

# --- Frontend HTML ---
@app.route('/')
def index():
    html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Indian Market Stock Analysis</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 0; padding: 0; background-color: #f9f9f9; color: #333; }
            h1 { text-align: center; background-color: #4CAF50; color: white; padding: 10px 0; margin: 0; }
            .controls { text-align: center; margin: 20px; }
            button { padding: 10px 20px; margin: 0 10px; font-size: 16px; cursor: pointer; border: none; border-radius: 5px; background-color: #008CBA; color: white; }
            button:disabled { background-color: #cccccc; cursor: not-allowed; }
            .stock-container { display: flex; flex-wrap: wrap; justify-content: center; margin-top: 20px; }
            .stock-box { width: 200px; margin: 10px; padding: 20px; text-align: center; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); color: white; }
            .symbol { font-size: 20px; font-weight: bold; }
            .price { font-size: 18px; font-weight: bold; margin: 10px 0; }
            .percent-change { font-size: 16px; }
            .summary { text-align: center; margin-top: 20px; font-size: 18px; padding: 20px; background: white; border-top: 2px solid #ddd; }
            #loading { text-align: center; font-size: 18px; display: none; color: #555; }
        </style>
    </head>
    <body>
        <h1 id="main-title">Market Analysis</h1>
        
        <div class="controls">
            <button id="btn-bank" onclick="switchIndex('banknifty', 'Bank Nifty')">Load Bank Nifty</button>
            <button id="btn-nifty" onclick="switchIndex('nifty50', 'Nifty 50')">Load Nifty 50</button>
        </div>

        <div id="loading">Fetching data, please wait...</div>

        <div class="stock-container" id="stock-container"></div>
        <div class="summary" id="summary"></div>

        <script>
            let currentEndpoint = '/api/banknifty';
            let fetchInterval;

            function getBoxColor(percentChange) {
                let red, green;
                if (percentChange > 0) {
                    red = 0; green = 128; 
                } else {
                    red = Math.min(255, 200 + Math.abs(percentChange) * 6);
                    green = Math.max(0, 255 - red);
                }
                return `rgb(${red}, ${green}, 0)`;
            }

            function switchIndex(endpoint, title) {
                currentEndpoint = `/api/${endpoint}`;
                document.getElementById('main-title').innerText = `${title} Analysis`;
                fetchStockData();
                
                // Reset interval to avoid overlapping fetches
                clearInterval(fetchInterval);
                fetchInterval = setInterval(fetchStockData, 10000); // Refreshes every 10 seconds
            }

            async function fetchStockData() {
                document.getElementById('loading').style.display = 'block';
                try {
                    const response = await fetch(currentEndpoint);
                    const { data } = await response.json();

                    const container = document.getElementById('stock-container');
                    container.innerHTML = '';

                    let positiveCount = 0; let negativeCount = 0;
                    let positiveTotalPercent = 0; let negativeTotalPercent = 0;
                    let totalPercent = 0;

                    data.forEach(stock => {
                        const stockBox = document.createElement('div');
                        stockBox.classList.add('stock-box');
                        stockBox.style.backgroundColor = getBoxColor(stock.percent_change);

                        stockBox.innerHTML = `
                            <div class="symbol">${stock.symbol}</div>
                            <div class="price">₹${stock.price.toFixed(2)}</div>
                            <div class="percent-change">${stock.percent_change.toFixed(2)}%</div>
                        `;
                        container.appendChild(stockBox);

                        if (stock.percent_change >= 0) {
                            positiveCount++; positiveTotalPercent += stock.percent_change;
                        } else {
                            negativeCount++; negativeTotalPercent += stock.percent_change;
                        }
                        totalPercent += stock.percent_change;
                    });

                    document.getElementById('summary').innerHTML = `
                        <p>Positive Stocks: <b>${positiveCount}</b> | Total Positive %: <span style="color:green;">${positiveTotalPercent.toFixed(2)}%</span></p>
                        <p>Negative Stocks: <b>${negativeCount}</b> | Total Negative %: <span style="color:red;">${negativeTotalPercent.toFixed(2)}%</span></p>
                        <p>Total Overall % Change: <b>${totalPercent.toFixed(2)}%</b></p>
                    `;
                } catch (err) {
                    console.error("Error:", err);
                } finally {
                    document.getElementById('loading').style.display = 'none';
                }
            }

            // Initial load
            switchIndex('banknifty', 'Bank Nifty');
        </script>
    </body>
    </html>
    """
    return render_template_string(html)

if __name__ == '__main__':
    app.run(debug=True)

