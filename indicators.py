\
from __future__ import annotations
import pandas as pd
import numpy as np

def add_sma(df: pd.DataFrame, period: int, col: str = "Close"):
    df[f"SMA{period}"] = df[col].rolling(period, min_periods=period//2).mean()
    return df

def _ema(series: pd.Series, span: int):
    return series.ewm(span=span, adjust=False).mean()

def add_rsi(df: pd.DataFrame, period: int = 14, col: str = "Close"):
    delta = df[col].diff()
    up = delta.clip(lower=0.0)
    down = -delta.clip(upper=0.0)
    roll_up = _ema(up, period)
    roll_down = _ema(down, period)
    rs = roll_up / (roll_down.replace(0, np.nan))
    rsi = 100.0 - (100.0 / (1.0 + rs))
    df[f"RSI{period}"] = rsi
    return df

def add_atr(df: pd.DataFrame, period: int = 14):
    high = df["High"]
    low = df["Low"]
    close = df["Close"]
    prev_close = close.shift(1)
    tr = pd.concat([
        (high - low).abs(),
        (high - prev_close).abs(),
        (low - prev_close).abs()
    ], axis=1).max(axis=1)
    atr = tr.ewm(alpha=1/period, adjust=False).mean()
    df[f"ATR{period}"] = atr
    return df

def vwap(intra: pd.DataFrame):
    tp = (intra["High"] + intra["Low"] + intra["Close"]) / 3.0
    cum_vol = intra["Volume"].cumsum().replace(0, np.nan)
    return (tp * intra["Volume"]).cumsum() / cum_vol

def pct(a, b):
    import math
    try:
        a = float(a)
        b = float(b)
        if b == 0.0 or math.isnan(b):
            return np.nan
        return (a - b) / b * 100.0
    except Exception:
        return np.nan

