from __future__ import annotations
import pathlib
from typing import List
import yfinance as yf

# Small fallbacks so the app still runs if yfinance list fetch fails
FALLBACK_SP500 = ["AAPL","MSFT","NVDA","AMZN","META","GOOGL","BRK-B","LLY","AVGO","JPM","XOM","JNJ","V","WMT","UNH"]
FALLBACK_NASDAQ100 = ["AAPL","MSFT","NVDA","AMZN","META","GOOGL","AVGO","TSLA","PEP","COST","ADBE","NFLX","AMD","INTC","CSCO"]

def _ensure_list(obj) -> List[str]:
    if obj is None:
        return []
    if isinstance(obj, (list, tuple, set)):
        return list(obj)
    # pandas Series / Index / DataFrame -> try to convert
    try:
        return list(obj)
    except Exception:
        return []

def load_universe(name_or_path: str) -> List[str]:
    p = pathlib.Path(name_or_path)
    if p.exists():
        return sorted({t.strip().upper() for t in p.read_text().splitlines() if t.strip()})

    name = (name_or_path or "").lower()
    try:
        if name == "sp500":
            lst = _ensure_list(yf.tickers_sp500())
            return lst if len(lst) > 0 else FALLBACK_SP500
        if name == "nasdaq100":
            # yfinance doesn't always have a clean N100 list; use broader NASDAQ as fallback
            lst = _ensure_list(yf.tickers_nasdaq())
            # Keep it reasonable: first 150 symbols, or fallback list
            return lst[:150] if len(lst) > 0 else FALLBACK_NASDAQ100
    except Exception:
        if name == "sp500":
            return FALLBACK_SP500
        if name == "nasdaq100":
            return FALLBACK_NASDAQ100

    raise ValueError(f"Unknown universe or missing file: {name_or_path}")
