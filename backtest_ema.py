import yfinance as yf
import pandas as pd
import pandas_ta as ta
from datetime import datetime, timedelta

def backtest_ema_crossover(ticker: str, years: int = 5, initial_capital: float = 1000.0):
    end = datetime.today()
    start = end - timedelta(days=365 * years)

    data = yf.download(ticker, start=start, end=end, auto_adjust=True)
    if data.empty:
        return None

    close = data["Close"]
    e13 = ta.ema(close, length=13)
    e50 = ta.ema(close, length=50)

    df = pd.DataFrame({
        "Close": close,
        "EMA13": e13,
        "EMA50": e50,
    }).dropna()

    df["CrossUp"] = (df["EMA13"].shift(1) <= df["EMA50"].shift(1)) & (df["EMA13"] > df["EMA50"])
    df["CrossDown"] = (df["EMA13"].shift(1) >= df["EMA50"].shift(1)) & (df["EMA13"] < df["EMA50"])

    capital = initial_capital
    position = 0.0
    trades = []

    for i in range(1, len(df)):
        row_prev = df.iloc[i - 1]
        row = df.iloc[i]

        if row_prev["CrossUp"] and position == 0.0:
            price = data["Open"].loc[row.name]
            position = capital / price
            capital = 0.0
            trades.append({"date": row.name, "side": "BUY", "price": float(price)})

        elif row_prev["CrossDown"] and position > 0.0:
            price = data["Open"].loc[row.name]
            capital = position * price
            position = 0.0
            trades.append({"date": row.name, "side": "SELL", "price": float(price)})

    final_value = capital
    if position > 0.0:
        last_price = data["Open"].iloc[-1]
        final_value = position * last_price

    total_return = (final_value / initial_capital) - 1.0
    years_actual = (df.index[-1] - df.index[0]).days / 365.0
    cagr = (final_value / initial_capital) ** (1 / years_actual) - 1.0 if years_actual > 0 else total_return

    return {
        "ticker": ticker,
        "initial_capital": initial_capital,
        "final_value": float(final_value),
        "total_return_pct": total_return * 100.0,
        "cagr_pct": cagr * 100.0,
        "trades": trades,
        "series": df.reset_index().to_dict(orient="records"),
    }
