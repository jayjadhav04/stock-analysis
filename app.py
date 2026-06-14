from flask import Flask, jsonify, render_template_string
from flask_cors import CORS
import yfinance as yf
import pandas as pd
import requests
import os

app = Flask(__name__)
CORS(app)

# --- Set up a highly disguised browser session ---
session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1"
})

# --- Lists of Stock Symbols ---
bank_nifty_symbols = [
    "HDFCBANK.NS", "ICICIBANK.NS", "SBIN.NS", "KOTAKBANK.NS", "AXISBANK.NS", 
    "BANKBARODA.NS", "PNB.NS", "CANBK.NS", "INDUSINDBK.NS", "FEDERALBNK.NS", "AUBANK.NS", "IDFCFIRSTB.NS"
]

nifty50_symbols = [
    "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "BHARTIARTL.NS", "ICICIBANK.NS", "INFY.NS", "SBIN.NS", "ITC.NS", "HINDUNILVR.NS", "LT.NS", "HCLTECH.NS", "SUNPHARMA.NS", "BAJFINANCE.NS", "M&M.NS", "NTPC.NS", "KOTAKBANK.NS", "AXISBANK.NS", "MARUTI.NS", "ULTRACEMCO.NS", "ONGC.NS", "WIPRO.NS", "TITAN.NS", "POWERGRID.NS", "TATAMOTORS.NS", "ADANIENT.NS", "ADANIPORTS.NS", "BAJAJFINSV.NS", "COALINDIA.NS", "BAJAJ-AUTO.NS", "JSWSTEEL.NS", "TRENT.NS", "BEL.NS", "ASIANPAINT.NS", "NESTLEIND.NS", "TATASTEEL.NS", "GRASIM.NS", "TECHM.NS", "HINDALCO.NS", "SBILIFE.NS", "HDFCLIFE.NS", "EICHERMOT.NS", "BPCL.NS", "SHRIRAMFIN.NS", "CIPLA.NS", "BRITANNIA.NS", "APOLLOHOSP.NS", "DRREDDY.NS", "HEROMOTOCO.NS", "TATACONSUM.NS", "INDUSINDBK.NS"
]

# --- Optimized Bulk Fetch Function ---
def fetch_stock_data(symbols):
    data = []
    errors = []
    try:
        # Fetch all symbols simultaneously
        df = yf.download(symbols, period="5d", progress=False, threads=False, session=session)
        
        if df.empty:
            return {"data": [], "errors": ["No data returned from Yahoo Finance."]}

        for symbol in symbols:
            try:
                closes = df['Close'][symbol].dropna()
                opens = df['Open'][symbol].dropna()
                
                if len(closes) > 1:
                    latest_close = float(closes.iloc[-1])
                    prev_close = float(closes.iloc[-2])
                    latest_open = float(opens.iloc[-1])

                    percent_change = ((latest_close - prev_close) / prev_close) * 100

                    data.append({
                        "symbol": symbol,
                        "price": latest_close,
                        "percent_change": percent_change,
                        "open_price": latest_open
                    })
                else:
                    errors.append(f"Not enough data for {symbol}")
            except Exception as e:
                errors.append(f"Error parsing {symbol}: {str(e)}")
                
    except Exception as e:
        errors.append(f"Bulk download error: {str(e)}")

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
            #loading { text-align: center; font-size: 18px; display: none; color: #555; font-weight: bold; }
            #error-box { text-align: center; color: red; font-weight: bold; margin-top: 10px; }
        </style>
    </head>
    <body>
        <h1 id="main-title">Market Analysis</h1>
        
        <div class="controls">
            <button id="btn-bank" onclick="switchIndex('banknifty', 'Bank Nifty')">Load Bank Nifty</button>
            <button id="btn-nifty" onclick="switchIndex('nifty50', 'Nifty 50')">Load Nifty 50</button>
        </div>

        <div id="loading">Fetching data, please wait...</div>
        <div id="error-box"></div>

        <div class="stock-container" id="stock-container"></div>
        <div class="summary" id="summary"></div>

                    let currentEndpoint = '/api/banknifty';
            let fetchInterval;
            let isInitialLoad = true; // Tracks if we need to show the loading text

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
                
                isInitialLoad = true; // Show loading screen when switching between indices
                fetchStockData();
                
                clearInterval(fetchInterval);
                // Refresh every 10 seconds silently
                fetchInterval = setInterval(() => {
                    isInitialLoad = false; // Don't wipe the screen for background updates
                    fetchStockData();
                }, 60000); 
            }

            async function fetchStockData() {
                if (isInitialLoad) {
                    document.getElementById('loading').style.display = 'block';
                    document.getElementById('stock-container').innerHTML = ''; 
                    document.getElementById('summary').innerHTML = '';
                }
                document.getElementById('error-box').innerText = ''; 

                try {
                    const response = await fetch(currentEndpoint);
                    
                    if (!response.ok) {
                        throw new Error(`Server returned status ${response.status}.`);
                    }

                    const { data, errors } = await response.json();

                    if (errors && errors.length > 0 && data.length === 0) {
                         throw new Error(errors[0]);
                    }

                    // Build the new HTML in memory first, so the screen doesn't go blank
                    let newContainerHTML = '';
                    let positiveCount = 0; let negativeCount = 0;
                    let positiveTotalPercent = 0; let negativeTotalPercent = 0;
                    let totalPercent = 0;

                    data.forEach(stock => {
                        const color = getBoxColor(stock.percent_change);
                        newContainerHTML += `
                            <div class="stock-box" style="background-color: ${color};">
                                <div class="symbol">${stock.symbol}</div>
                                <div class="price">₹${stock.price.toFixed(2)}</div>
                                <div class="percent-change">${stock.percent_change.toFixed(2)}%</div>
                            </div>
                        `;

                        if (stock.percent_change >= 0) {
                            positiveCount++; positiveTotalPercent += stock.percent_change;
                        } else {
                            negativeCount++; negativeTotalPercent += stock.percent_change;
                        }
                        totalPercent += stock.percent_change;
                    });

                    // Instantly swap the old data with the new data
                    document.getElementById('stock-container').innerHTML = newContainerHTML;
                    
                    document.getElementById('summary').innerHTML = `
                        <p>Positive Stocks: <b>${positiveCount}</b> | Total Positive %: <span style="color:green;">${positiveTotalPercent.toFixed(2)}%</span></p>
                        <p>Negative Stocks: <b>${negativeCount}</b> | Total Negative %: <span style="color:red;">${negativeTotalPercent.toFixed(2)}%</span></p>
                        <p>Total Overall % Change: <b>${totalPercent.toFixed(2)}%</b></p>
                    `;
                } catch (err) {
                    console.error("Fetch Error:", err);
                    document.getElementById('error-box').innerText = `Failed to load data: ${err.message}`;
                } finally {
                    document.getElementById('loading').style.display = 'none';
                }
            }

            // Start the app
            switchIndex('banknifty', 'Bank Nifty');

    </body>
    </html>
    """
    return render_template_string(html)

# --- Start Command for Render / Local Testing ---
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

