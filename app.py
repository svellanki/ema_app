from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from db import Base, engine, SessionLocal
from models import Signal, Position, Backtest
from screener_core import get_signals
from backtest_ema import backtest_ema_crossover

from datetime import datetime

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request):
    db = next(get_db())
    signals = db.query(Signal).order_by(Signal.scan_date.desc()).all()
    return templates.TemplateResponse("dashboard.html", {"request": request, "signals": signals})

@app.get("/scan")
def run_scan():
    db = next(get_db())
    signals = get_signals()
    for s in signals:
        bt = backtest_ema_crossover(s["ticker"])
        if not bt:
            continue

        backtest_row = db.query(Backtest).filter(Backtest.ticker == s["ticker"]).first()
        if not backtest_row:
            backtest_row = Backtest(ticker=s["ticker"])
        backtest_row.cagr_pct = bt["cagr_pct"]
        backtest_row.total_return_pct = bt["total_return_pct"]
        backtest_row.initial_capital = bt["initial_capital"]
        backtest_row.final_value = bt["final_value"]
        backtest_row.last_updated = datetime.utcnow()
        db.add(backtest_row)

        signal_row = Signal(
            ticker=s["ticker"],
            scan_date=s["scan_date"],
            close=s["close"],
            ema13=s["ema13"],
            ema50=s["ema50"],
            rsi=s["rsi"],
            macd_hist=s["macd_hist"],
            avg_vol_10=s["avg_vol_10"],
            market_cap=s["market_cap"],
            cagr_pct=bt["cagr_pct"],
            total_return_pct=bt["total_return_pct"],
            final_value=bt["final_value"],
        )
        db.add(signal_row)

        if bt["trades"]:
            first_trade = bt["trades"][0]
            if first_trade["side"] == "BUY":
                shares = bt["initial_capital"] / first_trade["price"]
                pos = Position(
                    ticker=s["ticker"],
                    entry_date=first_trade["date"],
                    entry_price=first_trade["price"],
                    shares=shares,
                    status="OPEN",
                )
                db.add(pos)

    db.commit()
    return RedirectResponse(url="/", status_code=303)

@app.get("/ticker/{symbol}", response_class=HTMLResponse)
def ticker_view(symbol: str, request: Request):
    db = next(get_db())
    bt = db.query(Backtest).filter(Backtest.ticker == symbol).first()
    if not bt:
        return RedirectResponse(url="/", status_code=303)

    bt_data = backtest_ema_crossover(symbol)
    return templates.TemplateResponse(
        "ticker.html",
        {
            "request": request,
            "ticker": symbol,
            "backtest": bt,
            "series": bt_data["series"],
            "trades": bt_data["trades"],
        },
    )

@app.get("/positions", response_class=HTMLResponse)
def positions_view(request: Request):
    db = next(get_db())
    positions = db.query(Position).all()
    return templates.TemplateResponse("positions.html", {"request": request, "positions": positions})
