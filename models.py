from sqlalchemy import Column, Integer, String, Float, DateTime
from db import Base
from datetime import datetime

class Signal(Base):
    __tablename__ = "signals"

    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String, index=True)
    scan_date = Column(DateTime, default=datetime.utcnow)
    close = Column(Float)
    ema13 = Column(Float)
    ema50 = Column(Float)
    rsi = Column(Float)
    macd_hist = Column(Float)
    avg_vol_10 = Column(Float)
    market_cap = Column(Float)
    cagr_pct = Column(Float)
    total_return_pct = Column(Float)
    final_value = Column(Float)

class Position(Base):
    __tablename__ = "positions"

    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String, index=True)
    entry_date = Column(DateTime)
    entry_price = Column(Float)
    shares = Column(Float)
    status = Column(String, default="OPEN")  # OPEN / CLOSED
    exit_date = Column(DateTime, nullable=True)
    exit_price = Column(Float, nullable=True)

class Backtest(Base):
    __tablename__ = "backtests"

    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String, unique=True, index=True)
    cagr_pct = Column(Float)
    total_return_pct = Column(Float)
    initial_capital = Column(Float)
    final_value = Column(Float)
    last_updated = Column(DateTime, default=datetime.utcnow)
