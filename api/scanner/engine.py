from __future__ import annotations

import concurrent.futures
import math
from typing import Any

import numpy as np
import pandas as pd
import pytz

from .config import SAMPLE_DATA_DIR
from .indicators import add_atr, add_rsi, add_sma, pct, vwap
from .rules import (
    bearish_engulfing,
    bullish_engulfing,
    doji,
    evening_star,
    hammer,
    harami_bear,
    harami_bull,
    higher_highs_lows,
    inverted_hammer,
    ma_stack_bullish,
    morning_star,
    shooting_star,
    spinning_top,
    three_black_crows,
    three_white_soldiers,
    volume_confirm,
    vwap_reclaim_premarket,
)

ET = pytz.timezone("America/New_York")


def slice_premarket(df: pd.DataFrame, start: str = "04:00", end: str = "09:29") -> pd.DataFrame:
    if df is None or df.empty:
        return df
    s_h, s_m = map(int, start.split(":"))
    e_h, e_m = map(int, end.split(":"))

    def in_premarket(ts: pd.Timestamp) -> bool:
        ts_et = ts.tz_convert(ET)
        value = ts_et.time()
        return (value.hour > s_h or (value.hour == s_h and value.minute >= s_m)) and (
            value.hour < e_h or (value.hour == e_h and value.minute <= e_m)
        )

    return df.loc[df.index.map(in_premarket)]


def _last_numeric_value(series: pd.Series | None) -> float:
    if series is None:
        return np.nan
    cleaned = series.dropna()
    if cleaned.empty:
        return np.nan
    return float(cleaned.iloc[-1])


class DataProvider:
    def __init__(self, cfg: dict[str, Any], mode: str = "live") -> None:
        self.cfg = cfg
        self.mode = mode

    def fetch(self, ticker: str) -> dict[str, Any]:
        if self.mode == "sample":
            return self._fetch_sample(ticker)
        return self._fetch_live(ticker)

    def _fetch_live(self, ticker: str) -> dict[str, Any]:
        try:
            import yfinance as yf
        except Exception:
            return {"ticker": ticker, "error": "yfinance not installed"}

        try:
            daily = yf.download(ticker, period="300d", interval="1d", auto_adjust=False, prepost=False, progress=False, threads=False)
            if daily is None or daily.empty:
                return {"ticker": ticker, "error": "no daily"}

            for period in self.cfg["indicators"].get("ma_periods", [20, 50, 200]):
                daily = add_sma(daily, period)
            daily = add_rsi(daily, self.cfg["indicators"].get("rsi_period", 14))
            daily = add_atr(daily, self.cfg["indicators"].get("atr_period", 14))

            intra = yf.download(ticker, period="1d", interval="1m", auto_adjust=False, prepost=True, progress=False, threads=False)
            pre = slice_premarket(intra, self.cfg["premarket_window"]["start"], self.cfg["premarket_window"]["end"])
            if pre is not None and not pre.empty:
                pre = pre.copy()
                pre["VWAP"] = vwap(pre)

            return self._package_payload(ticker, daily, pre)
        except Exception as exc:
            return {"ticker": ticker, "error": str(exc)}

    def _fetch_sample(self, ticker: str) -> dict[str, Any]:
        daily_path = SAMPLE_DATA_DIR / f"{ticker}_daily.csv"
        if not daily_path.exists():
            return {"ticker": ticker, "error": "no sample data"}

        daily = self._read_sample_csv(daily_path, "Date")
        for period in self.cfg["indicators"].get("ma_periods", [20, 50, 200]):
            daily = add_sma(daily, period)
        daily = add_rsi(daily, self.cfg["indicators"].get("rsi_period", 14))
        daily = add_atr(daily, self.cfg["indicators"].get("atr_period", 14))

        intraday_path = SAMPLE_DATA_DIR / f"{ticker}_intraday.csv"
        pre = pd.DataFrame()
        if intraday_path.exists():
            intra = self._read_sample_csv(intraday_path, "Datetime")
            if getattr(intra["Datetime"].dt, "tz", None) is None:
                intra["Datetime"] = intra["Datetime"].dt.tz_localize("America/New_York")
            else:
                intra["Datetime"] = intra["Datetime"].dt.tz_convert("America/New_York")
            intra = intra.set_index("Datetime")
            pre = slice_premarket(intra, self.cfg["premarket_window"]["start"], self.cfg["premarket_window"]["end"]).copy()
            if not pre.empty:
                pre["VWAP"] = vwap(pre)

        return self._package_payload(ticker, daily, pre)

    @staticmethod
    def _read_sample_csv(path, date_column: str) -> pd.DataFrame:
        frame = pd.read_csv(path, skiprows=[1] if _has_ticker_header(path) else None)
        frame[date_column] = pd.to_datetime(frame[date_column], errors="coerce")
        frame = frame.dropna(subset=[date_column]).copy()
        numeric_columns = [column for column in frame.columns if column != date_column]
        for column in numeric_columns:
            frame[column] = pd.to_numeric(frame[column], errors="coerce")
        return frame

    def _package_payload(self, ticker: str, daily: pd.DataFrame, pre: pd.DataFrame) -> dict[str, Any]:
        prev_close = _last_numeric_value(daily["Close"] if "Close" in daily else None)
        pre_last = _last_numeric_value(pre["Close"] if pre is not None and "Close" in pre else None)
        gap_pct = pct(pre_last, prev_close) if not math.isnan(prev_close) and not math.isnan(pre_last) else np.nan

        avg20_vol = float(daily["Volume"].tail(20).mean()) if "Volume" in daily else np.nan
        avg20_close = float(daily["Close"].tail(20).mean()) if "Close" in daily else np.nan
        avg20_dollar_vol = avg20_vol * avg20_close if not math.isnan(avg20_vol) and not math.isnan(avg20_close) else np.nan

        pre_dollar_volume = float((pre["Close"] * pre["Volume"]).sum()) if pre is not None and not pre.empty else np.nan
        baseline = max(avg20_dollar_vol * 0.05, 1.0) if not math.isnan(avg20_dollar_vol) else np.nan
        rel_dollar_vol = pre_dollar_volume / baseline if baseline and baseline > 0 else np.nan

        return {
            "ticker": ticker,
            "daily": daily,
            "pre": pre,
            "metrics": {
                "gap_pct": gap_pct,
                "avg20_dollar_vol": avg20_dollar_vol,
                "rel_dollar_vol": rel_dollar_vol,
                "price": prev_close,
                "premarket_last": pre_last,
            },
        }


def _has_ticker_header(path) -> bool:
    with open(path, "r", encoding="utf-8") as handle:
        handle.readline()
        second = handle.readline()
    return second.startswith(",")


def apply_filters(pkg: dict[str, Any], cfg: dict[str, Any]) -> tuple[bool, str]:
    if "error" in pkg:
        return False, pkg["error"]
    price = pkg["metrics"]["price"]
    if not (cfg["filters"]["min_price"] <= price <= cfg["filters"]["max_price"]):
        return False, "price range"
    if pkg["metrics"]["avg20_dollar_vol"] < cfg["filters"]["min_avg_dollar_vol"]:
        return False, "illiquid"
    return True, ""


def score(pkg: dict[str, Any], cfg: dict[str, Any]) -> tuple[int, list[str]]:
    daily = pkg["daily"]
    pre = pkg["pre"]
    metrics = pkg["metrics"]
    weights = cfg["scoring"]["weights"]
    bullish_only = cfg["scoring"].get("bullish_only", True)
    indecision_filter = cfg["scoring"].get("enable_indecision_filter", False)

    total = 0
    reasons: list[str] = []
    bullish_rules = [
        (hammer, "hammer"),
        (inverted_hammer, "inverted_hammer"),
        (bullish_engulfing, "bullish_engulfing"),
        (morning_star, "morning_star"),
        (harami_bull, "harami_bull"),
        (three_white_soldiers, "three_white_soldiers"),
    ]
    for fn, key in bullish_rules:
        ok, name = fn(daily)
        if ok:
            total += int(weights.get(key, 0))
            reasons.append(name)

    if indecision_filter:
        has_doji, _ = doji(daily)
        has_spinning_top, _ = spinning_top(daily)
        if has_doji or has_spinning_top:
            return 0, ["Indecision filter (Doji/Spinning Top)"]

    if not bullish_only:
        bearish_rules = [
            (shooting_star, "shooting_star"),
            (bearish_engulfing, "bearish_engulfing"),
            (evening_star, "evening_star"),
            (harami_bear, "harami_bear"),
            (three_black_crows, "three_black_crows"),
        ]
        for fn, key in bearish_rules:
            ok, name = fn(daily)
            if ok:
                total += int(weights.get(key, 0))
                reasons.append(name)

    if ma_stack_bullish(daily):
        total += int(weights.get("uptrend_ma_stack", 0))
        reasons.append("MA stack up")
    if higher_highs_lows(daily, lookback=12):
        total += int(weights.get("uptrend_hh_hl", 0))
        reasons.append("HH/HL uptrend")
    if vwap_reclaim_premarket(pre):
        total += int(weights.get("vwap_reclaim_pre", 0))
        reasons.append("Pre VWAP reclaim")
    if not math.isnan(metrics["gap_pct"]) and metrics["gap_pct"] >= 0.1:
        total += int(weights.get("gap_up", 0))
        reasons.append(f"Gap {metrics['gap_pct']:.2f}%")
    if volume_confirm(metrics["rel_dollar_vol"], min_mult=1.0):
        total += int(weights.get("volume_confirm", 0))
        reasons.append(f"Rel $Vol {metrics['rel_dollar_vol']:.2f}x")

    return total, reasons


def run_scan(tickers: list[str], cfg: dict[str, Any], mode: str = "live") -> pd.DataFrame:
    provider = DataProvider(cfg, mode=mode)
    packages: list[dict[str, Any]] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=16) as executor:
        futures = {executor.submit(provider.fetch, ticker): ticker for ticker in tickers}
        for future in concurrent.futures.as_completed(futures):
            packages.append(future.result())

    rows: list[dict[str, Any]] = []
    low_rows: list[dict[str, Any]] = []
    include_low = bool(cfg["scoring"].get("include_low_signal", True))
    low_cap = int(cfg["scoring"].get("low_signal_limit", 30))

    for pkg in packages:
        ok, _ = apply_filters(pkg, cfg)
        if not ok:
            continue
        total, reasons = score(pkg, cfg)
        metrics = pkg["metrics"]
        row = {
            "ticker": pkg["ticker"],
            "score": int(total),
            "gap_pct": metrics.get("gap_pct", np.nan),
            "rel_dollar_vol": metrics.get("rel_dollar_vol", np.nan),
            "avg20_dollar_vol": metrics.get("avg20_dollar_vol", np.nan),
            "price": metrics.get("price", np.nan),
            "premarket_last": metrics.get("premarket_last", np.nan),
            "reasons": reasons,
        }
        if total > 0:
            rows.append(row)
        elif include_low:
            low_rows.append(row)

    low_rows = sorted(
        low_rows,
        key=lambda row: row["rel_dollar_vol"] if pd.notna(row["rel_dollar_vol"]) else -1,
        reverse=True,
    )[:low_cap]
    rows.extend(low_rows)

    columns = ["ticker", "score", "gap_pct", "rel_dollar_vol", "avg20_dollar_vol", "price", "premarket_last", "reasons"]
    if not rows:
        return pd.DataFrame(columns=columns)

    result = pd.DataFrame(rows).sort_values(["score", "rel_dollar_vol", "gap_pct"], ascending=[False, False, False])
    top_n = int(cfg["scoring"].get("top_n", 100))
    return result.head(top_n).reset_index(drop=True)
