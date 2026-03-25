from __future__ import annotations

import pandas as pd


def last_n(df: pd.DataFrame, n: int = 3) -> pd.DataFrame | None:
    if df is None or len(df) < n:
        return None
    return df.iloc[-n:]


def body_abs(o: float, c: float) -> float:
    return abs(c - o)


def is_green(o: float, c: float) -> bool:
    return c > o


def is_red(o: float, c: float) -> bool:
    return c < o


def wick_upper(o: float, h: float, c: float) -> float:
    return h - max(o, c)


def wick_lower(o: float, l: float, c: float) -> float:
    return min(o, c) - l


def range_hl(h: float, l: float) -> float:
    return max(1e-9, h - l)


def long_lower_wick(o: float, h: float, l: float, c: float, min_ratio: float = 2.0) -> bool:
    lower = wick_lower(o, l, c)
    candle_body = body_abs(o, c)
    upper = wick_upper(o, h, c)
    return candle_body > 0 and lower / candle_body >= min_ratio and lower > upper


def long_upper_wick(o: float, h: float, l: float, c: float, min_ratio: float = 2.0) -> bool:
    upper = wick_upper(o, h, c)
    candle_body = body_abs(o, c)
    lower = wick_lower(o, l, c)
    return candle_body > 0 and upper / candle_body >= min_ratio and upper > lower


def small_body(o: float, h: float, l: float, c: float, frac: float = 0.3) -> bool:
    return body_abs(o, c) <= frac * range_hl(h, l)


def is_doji(o: float, h: float, l: float, c: float) -> bool:
    return body_abs(o, c) <= 0.1 * range_hl(h, l)


def is_spinning_top(o: float, h: float, l: float, c: float) -> bool:
    rng = range_hl(h, l)
    upper = wick_upper(o, h, c)
    lower = wick_lower(o, l, c)
    return body_abs(o, c) <= 0.3 * rng and upper >= 0.2 * rng and lower >= 0.2 * rng


def doji(df: pd.DataFrame) -> tuple[bool, str]:
    row = last_n(df, 1)
    if row is None:
        return False, ""
    o, h, l, c = map(float, row[["Open", "High", "Low", "Close"]].iloc[-1])
    return (True, "Doji") if is_doji(o, h, l, c) else (False, "")


def spinning_top(df: pd.DataFrame) -> tuple[bool, str]:
    row = last_n(df, 1)
    if row is None:
        return False, ""
    o, h, l, c = map(float, row[["Open", "High", "Low", "Close"]].iloc[-1])
    return (True, "Spinning Top") if is_spinning_top(o, h, l, c) else (False, "")


def hammer(df: pd.DataFrame) -> tuple[bool, str]:
    row = last_n(df, 1)
    if row is None:
        return False, ""
    o, h, l, c = map(float, row[["Open", "High", "Low", "Close"]].iloc[-1])
    return (True, "Hammer") if long_lower_wick(o, h, l, c, 2.0) else (False, "")


def inverted_hammer(df: pd.DataFrame) -> tuple[bool, str]:
    row = last_n(df, 1)
    if row is None:
        return False, ""
    o, h, l, c = map(float, row[["Open", "High", "Low", "Close"]].iloc[-1])
    ok = long_upper_wick(o, h, l, c, 2.0) and is_green(o, c)
    return (True, "Inverted Hammer") if ok else (False, "")


def bullish_engulfing(df: pd.DataFrame) -> tuple[bool, str]:
    row = last_n(df, 2)
    if row is None:
        return False, ""
    o1, c1 = map(float, row[["Open", "Close"]].iloc[-2])
    o2, c2 = map(float, row[["Open", "Close"]].iloc[-1])
    ok = is_red(o1, c1) and is_green(o2, c2) and o2 <= c1 and c2 >= o1
    return (True, "Bullish Engulfing") if ok else (False, "")


def morning_star(df: pd.DataFrame) -> tuple[bool, str]:
    row = last_n(df, 3)
    if row is None:
        return False, ""
    o1, c1, h1, l1 = map(float, row[["Open", "Close", "High", "Low"]].iloc[-3])
    o2, c2, h2, l2 = map(float, row[["Open", "Close", "High", "Low"]].iloc[-2])
    o3, c3, h3, l3 = map(float, row[["Open", "Close", "High", "Low"]].iloc[-1])
    ok = is_red(o1, c1) and small_body(o2, h2, l2, c2) and is_green(o3, c3) and c3 >= (o1 + c1) / 2.0
    return (True, "Morning Star") if ok else (False, "")


def harami_bull(df: pd.DataFrame) -> tuple[bool, str]:
    row = last_n(df, 2)
    if row is None:
        return False, ""
    o1, c1 = map(float, row[["Open", "Close"]].iloc[-2])
    o2, c2 = map(float, row[["Open", "Close"]].iloc[-1])
    prev_low, prev_high = min(o1, c1), max(o1, c1)
    cur_low, cur_high = min(o2, c2), max(o2, c2)
    ok = is_red(o1, c1) and cur_low >= prev_low and cur_high <= prev_high and is_green(o2, c2)
    return (True, "Bullish Harami") if ok else (False, "")


def three_white_soldiers(df: pd.DataFrame) -> tuple[bool, str]:
    row = last_n(df, 3)
    if row is None:
        return False, ""
    o1, c1 = map(float, row[["Open", "Close"]].iloc[-3])
    o2, c2 = map(float, row[["Open", "Close"]].iloc[-2])
    o3, c3 = map(float, row[["Open", "Close"]].iloc[-1])
    ok = all(is_green(*pair) for pair in [(o1, c1), (o2, c2), (o3, c3)]) and c2 > c1 and c3 > c2 and o2 > o1 and o3 > o2
    return (True, "Three White Soldiers") if ok else (False, "")


def shooting_star(df: pd.DataFrame) -> tuple[bool, str]:
    row = last_n(df, 1)
    if row is None:
        return False, ""
    o, h, l, c = map(float, row[["Open", "High", "Low", "Close"]].iloc[-1])
    return (True, "Shooting Star") if long_upper_wick(o, h, l, c, 2.0) else (False, "")


def bearish_engulfing(df: pd.DataFrame) -> tuple[bool, str]:
    row = last_n(df, 2)
    if row is None:
        return False, ""
    o1, c1 = map(float, row[["Open", "Close"]].iloc[-2])
    o2, c2 = map(float, row[["Open", "Close"]].iloc[-1])
    ok = is_green(o1, c1) and is_red(o2, c2) and o2 >= c1 and c2 <= o1
    return (True, "Bearish Engulfing") if ok else (False, "")


def evening_star(df: pd.DataFrame) -> tuple[bool, str]:
    row = last_n(df, 3)
    if row is None:
        return False, ""
    o1, c1, h1, l1 = map(float, row[["Open", "Close", "High", "Low"]].iloc[-3])
    o2, c2, h2, l2 = map(float, row[["Open", "Close", "High", "Low"]].iloc[-2])
    o3, c3, h3, l3 = map(float, row[["Open", "Close", "High", "Low"]].iloc[-1])
    ok = is_green(o1, c1) and small_body(o2, h2, l2, c2) and is_red(o3, c3) and c3 <= (o1 + c1) / 2.0
    return (True, "Evening Star") if ok else (False, "")


def harami_bear(df: pd.DataFrame) -> tuple[bool, str]:
    row = last_n(df, 2)
    if row is None:
        return False, ""
    o1, c1 = map(float, row[["Open", "Close"]].iloc[-2])
    o2, c2 = map(float, row[["Open", "Close"]].iloc[-1])
    prev_low, prev_high = min(o1, c1), max(o1, c1)
    cur_low, cur_high = min(o2, c2), max(o2, c2)
    ok = is_green(o1, c1) and cur_low >= prev_low and cur_high <= prev_high and is_red(o2, c2)
    return (True, "Bearish Harami") if ok else (False, "")


def three_black_crows(df: pd.DataFrame) -> tuple[bool, str]:
    row = last_n(df, 3)
    if row is None:
        return False, ""
    o1, c1 = map(float, row[["Open", "Close"]].iloc[-3])
    o2, c2 = map(float, row[["Open", "Close"]].iloc[-2])
    o3, c3 = map(float, row[["Open", "Close"]].iloc[-1])
    ok = all(is_red(*pair) for pair in [(o1, c1), (o2, c2), (o3, c3)]) and c2 < c1 and c3 < c2
    return (True, "Three Black Crows") if ok else (False, "")


def ma_stack_bullish(df: pd.DataFrame) -> bool:
    try:
        sma20 = float(df["SMA20"].iloc[-1])
        sma50 = float(df["SMA50"].iloc[-1])
        sma200 = float(df["SMA200"].iloc[-1])
        return sma20 > sma50 > sma200
    except Exception:
        return False


def higher_highs_lows(df: pd.DataFrame, lookback: int = 12) -> bool:
    try:
        if len(df) < lookback + 3:
            return False
        recent = df.tail(lookback + 3).copy()
        highs = recent["High"].rolling(3, min_periods=1).max()
        lows = recent["Low"].rolling(3, min_periods=1).min()
        return float(recent["High"].iloc[-1]) > float(highs.iloc[:-1].median()) and float(recent["Low"].iloc[-1]) > float(lows.iloc[:-1].median())
    except Exception:
        return False


def vwap_reclaim_premarket(pre_df: pd.DataFrame) -> bool:
    try:
        if pre_df is None or pre_df.empty or "VWAP" not in pre_df or "Close" not in pre_df:
            return False
        vwap_series = pre_df["VWAP"].dropna()
        close_series = pre_df["Close"].dropna()
        if vwap_series.empty or close_series.empty:
            return False
        return float(close_series.iloc[-1]) >= float(vwap_series.iloc[-1])
    except Exception:
        return False


def volume_confirm(rel_dollar_vol: float, min_mult: float = 1.0) -> bool:
    try:
        return float(rel_dollar_vol) >= float(min_mult)
    except Exception:
        return False
