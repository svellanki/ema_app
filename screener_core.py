from datetime import datetime
import yfinance as yf
import pandas as pd
import pandas_ta as ta

UNIVERSE = ["AAPL", "MSFT", "GOOGL", "AMZN", "META"]

def compute_indicators(ticker: str):
    data = yf.download(ticker, period="6mo", auto_adjust=True)
    if data.empty:
        return None

    close = data["Close"]
    ema13 = ta.ema(close, length=13)
    ema50 = ta.ema(close, length=50)
    rsi = ta.rsi(close, length=14)
    macd = ta.macd(close)
    macd_hist = macd["MACDh_12_26_9"] if macd is not None else None
    avg_vol_10 = data["Volume"].rolling(10).mean().iloc[-1]

    return {
        "ticker": ticker,
        "close": float(close.iloc[-1]),
        "ema13": float(ema13.iloc[-1]),
        "ema50": float(ema50.iloc[-1]),
        "rsi": float(rsi.iloc[-1]),
        "macd_hist": float(macd_hist.iloc[-1]) if macd_hist is not None else None,
        "avg_vol_10": float(avg_vol_10),
        "market_cap": None,
    }

def get_signals():
    signals = []
    for t in UNIVERSE:
        ind = compute_indicators(t)
        if not ind:
            continue
        if ind["ema13"] > ind["ema50"]:
            ind["scan_date"] = datetime.utcnow()
            signals.append(ind)
    return signals
