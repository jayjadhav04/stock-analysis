# Stock Analysis – Nifty50 & BankNifty 📈

A real-time stock market analysis web application built using **Python**, **Flask**, and **Yahoo Finance API (`yfinance`)**.

This project tracks live data for **Nifty50** and **BankNifty** stocks, displaying:

- Current stock price
- Percentage change
- Opening price
- Positive/negative market movement
- Real-time updates every 10 seconds

The UI uses color-coded stock cards for quick visualization of market performance.

---

# 🚀 Features

✅ Real-time stock market data using Yahoo Finance API  
✅ Separate analysis for **Nifty50** and **BankNifty**  
✅ Auto-refresh stock data every 10 seconds  
✅ Responsive and clean dashboard UI  

### Color Indication
- 🟢 Green → Positive movement
- 🔴 Red → Negative movement

### Dashboard Displays
- Current Price
- Percentage Change
- Market Summary
- Positive vs Negative Stocks

---

# 🛠️ Tech Stack

- Python
- Flask
- HTML/CSS
- Yahoo Finance API (`yfinance`)

---

# 📷 Project Screenshots

## 🔹 Nifty50 Stock Analysis Dashboard

![Nifty50 Dashboard](Screenshot/Screenshot%20(126)n.png)

---

## 🔹 BankNifty Stock Analysis Dashboard

![BankNifty Dashboard](Screenshot/Screenshot%20(127).png)

---

# 📂 Project Structure

```bash
stock-analysis/
│
├── BANK_NIFTY.py
├── NIFTY50.py
├── requirements.txt
├── README.md
│
└── Screenshot/
    ├── Screenshot (126).png
    └── Screenshot (127).png
```

---

# ⚙️ Installation

## 1️⃣ Clone the Repository

```bash
git clone https://github.com/jayjadhav04/stock-analysis.git
```

---

## 2️⃣ Navigate to Project Directory

```bash
cd stock-analysis
```

---

## 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

---

# ▶️ Run the Project

## Run Nifty50 Analysis

```bash
python NIFTY50.py
```

---

## Run BankNifty Analysis

```bash
python BANK_NIFTY.py
```

---

# 🌐 Open in Browser

After running the application, open:

```bash
http://127.0.0.1:5000
```

---

# 📊 How It Works

The application fetches live stock data using the `yfinance` library.

For every stock:
- Current market price is fetched
- Percentage change is calculated
- Stock cards are dynamically generated
- Dashboard updates automatically every 10 seconds

---

# 🔮 Future Improvements

- Add candlestick charts
- Add stock search functionality
- Deploy on Render/Heroku/Vercel
- Add database support
- Add AI-based stock prediction
- Mobile responsive UI improvements

---

# 🤝 Contributing

Contributions are welcome!

1. Fork the repository
2. Create a new branch
3. Commit your changes
4. Push to your branch
5. Create a Pull Request

---

# 👨‍💻 Author

**Jay Dnyaneshwar Jadhav**

- GitHub: [jayjadhav04](https://github.com/jayjadhav04)

---

# ⭐ Support

If you like this project, give it a ⭐ on GitHub.
