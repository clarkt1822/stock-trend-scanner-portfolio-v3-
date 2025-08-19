\
from __future__ import annotations
import concurrent.futures, math
from typing import Dict, Any, List
import pandas as pd
import numpy as np
import pytz

from indicators import add_sma, add_rsi, add_atr, vwap, pct
from rules_cheatsheet import (
    hammer, inverted_hammer, bullish_engulfing, morning_star, harami_bull, three_white_soldiers,
    shooting_star, bearish_engulfing, evening_star, harami_bear, three_black_crows,
    doji, spinning_top, ma_stack_bullish, higher_highs_lows, vwap_reclaim_premarket, volume_confirm
)

ET = pytz.timezone("America/New_York")

def slice_premarket(df: pd.DataFrame, start="04:00", end="09:29"):
    if df is None or df.empty:
        return df
    s_h, s_m = map(int, start.split(":"))
    e_h, e_m = map(int, end.split(":"))
    def in_pre(ts):
        ts_et = ts.tz_convert(ET)
        t = ts_et.time()
        return (t.hour > s_h or (t.hour == s_h and t.minute >= s_m)) and \
               (t.hour < e_h or (t.hour == e_h and t.minute <= e_m))
    return df.loc[df.index.map(in_pre)]

class DataProvider:
    def __init__(self, cfg: Dict[str, Any], mode: str = "live"):
        self.cfg = cfg
        self.mode = mode

    def fetch(self, ticker: str) -> Dict[str, Any]:
        if self.mode == "sample":
            return self._fetch_sample(ticker)
        return self._fetch_live(ticker)

    def _fetch_live(self, ticker: str) -> Dict[str, Any]:
        try:
            import yfinance as yf
        except Exception:
            return {"ticker": ticker, "error": "yfinance not installed"}
        try:
            daily = yf.download(ticker, period="300d", interval="1d", auto_adjust=False, prepost=False, progress=False, threads=False)
            if daily is None or daily.empty: return {"ticker": ticker, "error": "no daily"}
            for p in self.cfg["indicators"].get("ma_periods", [20,50,200]):
                daily = add_sma(daily, p)
            daily = add_rsi(daily, self.cfg["indicators"].get("rsi_period", 14))
            daily = add_atr(daily, self.cfg["indicators"].get("atr_period", 14))

            intra = yf.download(ticker, period="1d", interval="1m", auto_adjust=False, prepost=True, progress=False, threads=False)
            pre = slice_premarket(intra, self.cfg["premarket_window"]["start"], self.cfg["premarket_window"]["end"])
            if pre is not None and not pre.empty:
                pre = pre.copy()
                pre["VWAP"] = vwap(pre)

            prev_close = float(daily["Close"].iloc[-1]) if not daily.empty else np.nan
            pre_last = float(pre["Close"].dropna().iloc[-1]) if pre is not None and not pre.empty else np.nan
            gap_pct = pct(pre_last, prev_close) if (not math.isnan(pre_last) and not math.isnan(prev_close)) else np.nan

            avg20_vol = float(daily["Volume"].tail(20).mean()) if "Volume" in daily else np.nan
            avg20_close = float(daily["Close"].tail(20).mean()) if "Close" in daily else np.nan
            avg20_dollar_vol = avg20_vol * avg20_close if (not math.isnan(avg20_vol) and not math.isnan(avg20_close)) else np.nan

            pre_dv_today = float((pre["Close"] * pre["Volume"]).sum()) if pre is not None and not pre.empty else np.nan
            baseline = max(avg20_dollar_vol * 0.05, 1.0) if not math.isnan(avg20_dollar_vol) else np.nan
            rel_dollar_vol = pre_dv_today / baseline if (baseline and baseline > 0) else np.nan

            return {
                "ticker": ticker,
                "daily": daily,
                "pre": pre,
                "metrics": {
                    "gap_pct": gap_pct,
                    "avg20_dollar_vol": avg20_dollar_vol,
                    "rel_dollar_vol": rel_dollar_vol,
                    "price": prev_close,
                }
            }
        except Exception as e:
            return {"ticker": ticker, "error": str(e)}

    def _fetch_sample(self, ticker: str) -> Dict[str, Any]:
        import pathlib
        base = pathlib.Path(__file__).parent / "sample_data"
        dfile = base / f"{ticker}_daily.csv"
        if not dfile.exists():
            return {"ticker": ticker, "error": "no sample data"}
        daily = pd.read_csv(dfile, parse_dates=["Date"]).set_index("Date")
        for p in self.cfg["indicators"].get("ma_periods", [20,50,200]):
            daily = add_sma(daily, p)
        daily = add_rsi(daily, self.cfg["indicators"].get("rsi_period", 14))
        daily = add_atr(daily, self.cfg["indicators"].get("atr_period", 14))

        prefile = base / f"{ticker}_intraday.csv"
        if prefile.exists():
            intra = pd.read_csv(prefile, parse_dates=["Datetime"])
            if getattr(intra["Datetime"].dt, "tz", None) is None:
                intra["Datetime"] = intra["Datetime"].dt.tz_localize("America/New_York")
            else:
                intra["Datetime"] = intra["Datetime"].dt.tz_convert("America/New_York")
            intra = intra.set_index("Datetime")
            pre = slice_premarket(intra, self.cfg["premarket_window"]["start"], self.cfg["premarket_window"]["end"]).copy()
            if not pre.empty:
                from indicators import vwap as _vwap
                pre["VWAP"] = _vwap(pre)
        else:
            pre = pd.DataFrame()

        prev_close = float(daily["Close"].iloc[-1]) if not daily.empty else np.nan
        pre_last = float(pre["Close"].dropna().iloc[-1]) if pre is not None and not pre.empty else np.nan
        gap_pct = pct(pre_last, prev_close) if (not math.isnan(pre_last) and not math.isnan(prev_close)) else np.nan

        avg20_vol = float(daily["Volume"].tail(20).mean()) if "Volume" in daily else np.nan
        avg20_close = float(daily["Close"].tail(20).mean()) if "Close" in daily else np.nan
        avg20_dollar_vol = avg20_vol * avg20_close if (not math.isnan(avg20_vol) and not math.isnan(avg20_close)) else np.nan

        pre_dv_today = float((pre["Close"] * pre["Volume"]).sum()) if pre is not None and not pre.empty else np.nan
        baseline = max(avg20_dollar_vol * 0.05, 1.0) if not math.isnan(avg20_dollar_vol) else np.nan
        rel_dollar_vol = pre_dv_today / baseline if (baseline and baseline > 0) else np.nan

        return {
            "ticker": ticker,
            "daily": daily,
            "pre": pre,
            "metrics": {
                "gap_pct": gap_pct,
                "avg20_dollar_vol": avg20_dollar_vol,
                "rel_dollar_vol": rel_dollar_vol,
                "price": prev_close,
            }
        }

def apply_filters(pkg: Dict[str, Any], cfg: Dict[str, Any]) -> tuple[bool, str]:
    if "error" in pkg: return (False, pkg["error"])
    price = pkg["metrics"]["price"]
    if not (cfg["filters"]["min_price"] <= price <= cfg["filters"]["max_price"]):
        return (False, "price range")
    if pkg["metrics"]["avg20_dollar_vol"] < cfg["filters"]["min_avg_dollar_vol"]:
        return (False, "illiquid")
    return (True, "")

def score(pkg: Dict[str, Any], cfg: Dict[str, Any]) -> tuple[int, list[str]]:
    d = pkg["daily"]; pre = pkg["pre"]; m = pkg["metrics"]
    w = cfg["scoring"]["weights"]
    bullish_only = cfg["scoring"].get("bullish_only", True)
    indecision_filter = cfg["scoring"].get("enable_indecision_filter", False)

    total = 0; reasons = []

    # bullish patterns
    for fn, key in [(hammer,"hammer"), (inverted_hammer,"inverted_hammer"),
                    (bullish_engulfing,"bullish_engulfing"), (morning_star,"morning_star"),
                    (harami_bull,"harami_bull"), (three_white_soldiers,"three_white_soldiers")]:
        ok, name = fn(d)
        if ok: total += int(w.get(key, 0)); reasons.append(name)

    # indecision optional filter
    if indecision_filter:
        from rules_cheatsheet import doji, spinning_top
        ok_i, _ = doji(d); ok_s, _ = spinning_top(d)
        if ok_i or ok_s:
            return (0, ["Indecision filter (Doji/Spinning Top)"])

    # bearish (optional)
    if not bullish_only:
        for fn, key in [(shooting_star,"shooting_star"), (bearish_engulfing,"bearish_engulfing"),
                        (evening_star,"evening_star"), (harami_bear,"harami_bear"),
                        (three_black_crows,"three_black_crows")]:
            ok, name = fn(d)
            if ok: total += int(w.get(key, 0)); reasons.append(name)

    # trend & confirmations (relaxed thresholds)
    if ma_stack_bullish(d):
        total += int(w.get("uptrend_ma_stack", 0)); reasons.append("MA stack up")
    if higher_highs_lows(d, lookback=12):
        total += int(w.get("uptrend_hh_hl", 0)); reasons.append("HH/HL uptrend")
    if vwap_reclaim_premarket(pre):
        total += int(w.get("vwap_reclaim_pre", 0)); reasons.append("Pre VWAP reclaim")
    if not math.isnan(m["gap_pct"]) and m["gap_pct"] >= 0.1:   # relaxed 0.1%
        total += int(w.get("gap_up", 0)); reasons.append(f"Gap {m['gap_pct']:.2f}%")
    if volume_confirm(m["rel_dollar_vol"], min_mult=1.0):      # relaxed 1.0x
        total += int(w.get("volume_confirm", 0)); reasons.append(f"Rel $Vol {m['rel_dollar_vol']:.2f}x")

    return total, reasons

def run_scan(tickers: List[str], cfg: Dict[str, Any], mode: str = "live") -> pd.DataFrame:
    provider = DataProvider(cfg, mode=mode)
    pkgs: List[Dict[str, Any]] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=16) as ex:
        futs = {ex.submit(provider.fetch, t): t for t in tickers}
        for fut in concurrent.futures.as_completed(futs):
            pkgs.append(fut.result())

    rows = []
    include_low = bool(cfg["scoring"].get("include_low_signal", True))
    low_cap = int(cfg["scoring"].get("low_signal_limit", 30))
    low_rows = []

    for pkg in pkgs:
        ok, why = apply_filters(pkg, cfg)
        if not ok: 
            continue
        s, reasons = score(pkg, cfg)
        m = pkg["metrics"]
        row = {
            "ticker": pkg["ticker"],
            "score": int(s),
            "gap_pct": m.get("gap_pct", np.nan),
            "rel_dollar_vol": m.get("rel_dollar_vol", np.nan),
            "avg20_dollar_vol": m.get("avg20_dollar_vol", np.nan),
            "reasons": "; ".join(reasons) if reasons else "",
        }
        if s > 0:
            rows.append(row)
        elif include_low:
            low_rows.append(row)

    # combine rows; limit low-signal tail
    low_rows = sorted(low_rows, key=lambda r: (r["rel_dollar_vol"] if pd.notna(r["rel_dollar_vol"]) else -1), reverse=True)[:low_cap]
    rows.extend(low_rows)

    if not rows:
        return pd.DataFrame(columns=["ticker","score","gap_pct","rel_dollar_vol","avg20_dollar_vol","reasons"])
    df = pd.DataFrame(rows).sort_values(["score","rel_dollar_vol","gap_pct"], ascending=[False,False,False])
    top_n = int(cfg["scoring"].get("top_n", 100))
    return df.head(top_n)
