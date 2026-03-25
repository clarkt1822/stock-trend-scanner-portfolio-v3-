from __future__ import annotations

import pandas as pd
import numpy as np


def add_sma(df: pd.DataFrame, period: int, col: str = "Close") -> pd.DataFrame:
    df[f"SMA{period}"] = df[col].rolling(period, min_periods=period // 2).mean()
    return df


def _ema(series: pd.Series, span: int) -> pd.Series:
    return series.ewm(span=span, adjust=False).mean()


def add_rsi(df: pd.DataFrame, period: int = 14, col: str = "Close") -> pd.DataFrame:
    delta = df[col].diff()
    up = delta.clip(lower=0.0)
    down = -delta.clip(upper=0.0)
    roll_up = _ema(up, period)
    roll_down = _ema(down, period)
    rs = roll_up / roll_down.replace(0, np.nan)
    df[f"RSI{period}"] = 100.0 - (100.0 / (1.0 + rs))
    return df


def add_atr(df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
    high = df["High"]
    low = df["Low"]
    close = df["Close"]
    prev_close = close.shift(1)
    tr = pd.concat(
        [
            (high - low).abs(),
            (high - prev_close).abs(),
            (low - prev_close).abs(),
        ],
        axis=1,
    ).max(axis=1)
    df[f"ATR{period}"] = tr.ewm(alpha=1 / period, adjust=False).mean()
    return df


def vwap(intra: pd.DataFrame) -> pd.Series:
    typical_price = (intra["High"] + intra["Low"] + intra["Close"]) / 3.0
    cumulative_volume = intra["Volume"].cumsum().replace(0, np.nan)
    return (typical_price * intra["Volume"]).cumsum() / cumulative_volume


def pct(a: float | int | None, b: float | int | None) -> float:
    import math

    try:
        lhs = float(a)
        rhs = float(b)
        if rhs == 0.0 or math.isnan(rhs):
            return np.nan
        return (lhs - rhs) / rhs * 100.0
    except Exception:
        return np.nan
