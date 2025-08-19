from __future__ import annotations
import pandas as pd
import numpy as np

# ------------------ Helpers ------------------ #
def last_n(df: pd.DataFrame, n: int = 3):
    if df is None or len(df) < n:
        return None
    return df.iloc[-n:]

def body(o, c): return c - o
def body_abs(o, c): return abs(c - o)
def is_green(o, c): return c > o
def is_red(o, c):   return c < o

def wick_upper(o, h, c): return h - max(o, c)
def wick_lower(o, l, c): return min(o, c) - l
def range_hl(h, l):      return max(1e-9, h - l)

def long_lower_wick(o, h, l, c, min_ratio=2.0):
    lower = wick_lower(o, l, c)
    b = body_abs(o, c)
    upper = wick_upper(o, h, c)
    return b > 0 and lower / b >= min_ratio and lower > upper

def long_upper_wick(o, h, l, c, min_ratio=2.0):
    upper = wick_upper(o, h, c)
    b = body_abs(o, c)
    lower = wick_lower(o, l, c)
    return b > 0 and upper / b >= min_ratio and upper > lower

def small_body(o, h, l, c, frac=0.3):
    rng = range_hl(h, l)
    return body_abs(o, c) <= frac * rng

def is_doji(o, h, l, c):
    rng = range_hl(h, l)
    return body_abs(o, c) <= 0.1 * rng

def is_spinning_top(o, h, l, c):
    rng = range_hl(h, l)
    b = body_abs(o, c)
    up = wick_upper(o, h, c)
    lo = wick_lower(o, l, c)
    return b <= 0.3 * rng and up >= 0.2 * rng and lo >= 0.2 * rng

# ------------------ Indecision ------------------ #
def doji(df: pd.DataFrame):
    r = last_n(df, 1)
    if r is None: return (False, "")
    o, h, l, c = map(float, r[["Open","High","Low","Close"]].iloc[-1])
    ok = is_doji(o, h, l, c)
    return (ok, "Doji") if ok else (False, "")

def spinning_top(df: pd.DataFrame):
    r = last_n(df, 1)
    if r is None: return (False, "")
    o, h, l, c = map(float, r[["Open","High","Low","Close"]].iloc[-1])
    ok = is_spinning_top(o, h, l, c)
    return (ok, "Spinning Top") if ok else (False, "")

# ------------------ Bullish Patterns ------------------ #
def hammer(df: pd.DataFrame):
    r = last_n(df, 1)
    if r is None: return (False, "")
    o, h, l, c = map(float, r[["Open","High","Low","Close"]].iloc[-1])
    ok = long_lower_wick(o, h, l, c, 2.0)
    return (ok, "Hammer") if ok else (False, "")

def inverted_hammer(df: pd.DataFrame):
    r = last_n(df, 1)
    if r is None: return (False, "")
    o, h, l, c = map(float, r[["Open","High","Low","Close"]].iloc[-1])
    ok = long_upper_wick(o, h, l, c, 2.0) and is_green(o, c)
    return (ok, "Inverted Hammer") if ok else (False, "")

def bullish_engulfing(df: pd.DataFrame):
    r = last_n(df, 2)
    if r is None: return (False, "")
    o1, c1, h1, l1 = map(float, r[["Open","Close","High","Low"]].iloc[-2])
    o2, c2, h2, l2 = map(float, r[["Open","Close","High","Low"]].iloc[-1])
    ok = is_red(o1, c1) and is_green(o2, c2) and (o2 <= c1) and (c2 >= o1)
    return (ok, "Bullish Engulfing") if ok else (False, "")

def morning_star(df: pd.DataFrame):
    r = last_n(df, 3)
    if r is None: return (False, "")
    o1, c1, h1, l1 = map(float, r[["Open","Close","High","Low"]].iloc[-3])
    o2, c2, h2, l2 = map(float, r[["Open","Close","High","Low"]].iloc[-2])
    o3, c3, h3, l3 = map(float, r[["Open","Close","High","Low"]].iloc[-1])
    small2 = small_body(o2, h2, l2, c2)
    ok = is_red(o1, c1) and small2 and is_green(o3, c3) and c3 >= (o1 + c1)/2.0
    return (ok, "Morning Star") if ok else (False, "")

def harami_bull(df: pd.DataFrame):
    r = last_n(df, 2)
    if r is None: return (False, "")
    o1, c1 = map(float, r[["Open","Close"]].iloc[-2])
    o2, c2, h2, l2 = map(float, r[["Open","Close","High","Low"]].iloc[-1])
    prev_low, prev_high = min(o1, c1), max(o1, c1)
    cur_low,  cur_high  = min(o2, c2), max(o2, c2)
    ok = is_red(o1, c1) and (cur_low >= prev_low) and (cur_high <= prev_high) and is_green(o2, c2)
    return (ok, "Bullish Harami") if ok else (False, "")

def three_white_soldiers(df: pd.DataFrame):
    r = last_n(df, 3)
    if r is None: return (False, "")
    o1, c1 = map(float, r[["Open","Close"]].iloc[-3])
    o2, c2 = map(float, r[["Open","Close"]].iloc[-2])
    o3, c3 = map(float, r[["Open","Close"]].iloc[-1])
    cond = all([is_green(*x) for x in [(o1,c1),(o2,c2),(o3,c3)]]) and (c2 > c1) and (c3 > c2) and (o2 > o1) and (o3 > o2)
    return (cond, "Three White Soldiers") if cond else (False, "")

# ------------------ Bearish Patterns ------------------ #
def shooting_star(df: pd.DataFrame):
    r = last_n(df, 1)
    if r is None: return (False, "")
    o, h, l, c = map(float, r[["Open","High","Low","Close"]].iloc[-1])
    ok = long_upper_wick(o, h, l, c, 2.0)
    return (ok, "Shooting Star") if ok else (False, "")

def bearish_engulfing(df: pd.DataFrame):
    r = last_n(df, 2)
    if r is None: return (False, "")
    o1, c1 = map(float, r[["Open","Close"]].iloc[-2])
    o2, c2 = map(float, r[["Open","Close"]].iloc[-1])
    ok = is_green(o1, c1) and is_red(o2, c2) and (o2 >= c1) and (c2 <= o1)
    return (ok, "Bearish Engulfing") if ok else (False, "")

def evening_star(df: pd.DataFrame):
    r = last_n(df, 3)
    if r is None: return (False, "")
    o1, c1, h1, l1 = map(float, r[["Open","Close","High","Low"]].iloc[-3])
    o2, c2, h2, l2 = map(float, r[["Open","Close","High","Low"]].iloc[-2])
    o3, c3, h3, l3 = map(float, r[["Open","Close","High","Low"]].iloc[-1])
    small2 = small_body(o2, h2, l2, c2)
    ok = is_green(o1, c1) and small2 and is_red(o3, c3) and c3 <= (o1 + c1)/2.0
    return (ok, "Evening Star") if ok else (False, "")

def harami_bear(df: pd.DataFrame):
    r = last_n(df, 2)
    if r is None: return (False, "")
    o1, c1 = map(float, r[["Open","Close"]].iloc[-2])
    o2, c2, h2, l2 = map(float, r[["Open","Close","High","Low"]].iloc[-1])
    prev_low, prev_high = min(o1, c1), max(o1, c1)
    cur_low,  cur_high  = min(o2, c2), max(o2, c2)
    ok = is_green(o1, c1) and (cur_low >= prev_low) and (cur_high <= prev_high) and is_red(o2, c2)
    return (ok, "Bearish Harami") if ok else (False, "")

def three_black_crows(df: pd.DataFrame):
    r = last_n(df, 3)
    if r is None: return (False, "")
    o1, c1 = map(float, r[["Open","Close"]].iloc[-3])
    o2, c2 = map(float, r[["Open","Close"]].iloc[-2])
    o3, c3 = map(float, r[["Open","Close"]].iloc[-1])
    cond = all([is_red(*x) for x in [(o1,c1),(o2,c2),(o3,c3)]]) and (c2 < c1) and (c3 < c2)
    return (cond, "Three Black Crows") if cond else (False, "")

# ------------------ Trend & Confirmation ------------------ #
def ma_stack_bullish(df: pd.DataFrame):
    # Force scalar floats to avoid pandas truth-value ambiguity
    try:
        s20 = float(df["SMA20"].iloc[-1])
        s50 = float(df["SMA50"].iloc[-1])
        s200 = float(df["SMA200"].iloc[-1])
        return (s20 > s50) and (s50 > s200)
    except Exception:
        return False

def higher_highs_lows(df: pd.DataFrame, lookback: int = 12):
    try:
        if len(df) < lookback + 3:
            return False
        recent = df.tail(lookback + 3).copy()
        highs = recent["High"].rolling(3, min_periods=1).max()
        lows  = recent["Low"].rolling(3, min_periods=1).min()
        last_high = float(recent["High"].iloc[-1])
        last_low  = float(recent["Low"].iloc[-1])
        prior_high_med = float(highs.iloc[:-1].median()) if len(highs) > 1 else last_high
        prior_low_med  = float(lows.iloc[:-1].median())  if len(lows)  > 1 else last_low
        return (last_high > prior_high_med) and (last_low > prior_low_med)
    except Exception:
        return False

def vwap_reclaim_premarket(pre_df: pd.DataFrame):
    # Be robust to missing/empty premarket data
    try:
        if pre_df is None or pre_df.empty:
            return False
        if "VWAP" not in pre_df or "Close" not in pre_df:
            return False
        vwap_series = pre_df["VWAP"].dropna()
        close_series = pre_df["Close"].dropna()
        if vwap_series.empty or close_series.empty:
            return False
        last_vwap = float(vwap_series.iloc[-1])
        last_close = float(close_series.iloc[-1])
        return last_close >= last_vwap
    except Exception:
        return False

def volume_confirm(rel_dollar_vol: float, min_mult: float = 1.0):
    try:
        return float(rel_dollar_vol) >= float(min_mult)
    except Exception:
        return False
