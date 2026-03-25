from __future__ import annotations

from pathlib import Path
from typing import Iterable

import yfinance as yf

from .config import UNIVERSES_DIR

FALLBACK_SP500 = ["AAPL", "MSFT", "NVDA", "AMZN", "META", "GOOGL", "BRK-B", "LLY", "AVGO", "JPM", "XOM", "JNJ", "V", "WMT", "UNH"]
FALLBACK_NASDAQ100 = ["AAPL", "MSFT", "NVDA", "AMZN", "META", "GOOGL", "AVGO", "TSLA", "PEP", "COST", "ADBE", "NFLX", "AMD", "INTC", "CSCO"]


class UniverseNotFoundError(ValueError):
    pass


def _ensure_list(obj: object) -> list[str]:
    if obj is None:
        return []
    if isinstance(obj, (list, tuple, set)):
        return [str(item) for item in obj]
    try:
        return [str(item) for item in obj]  # type: ignore[arg-type]
    except Exception:
        return []


def _normalize_symbols(values: Iterable[str]) -> list[str]:
    return sorted({value.strip().upper() for value in values if str(value).strip()})


def _read_universe_file(path: Path) -> list[str]:
    lines = [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if not lines:
        return []

    normalized_lines = [line.split(",")[0].strip() for line in lines]
    if normalized_lines and normalized_lines[0].lower() in {"ticker", "symbol"}:
        normalized_lines = normalized_lines[1:]
    return _normalize_symbols(normalized_lines)


def list_universe_options() -> list[dict[str, str | int]]:
    dynamic = [
        {"id": "sp500", "label": "S&P 500", "kind": "dynamic"},
        {"id": "nasdaq100", "label": "NASDAQ 100", "kind": "dynamic"},
    ]
    file_universes = []
    for path in sorted(UNIVERSES_DIR.glob("*.csv")):
        tickers = load_universe(path.name)
        file_universes.append(
            {
                "id": path.name,
                "label": path.stem.replace("_", " ").title(),
                "kind": "file",
                "count": len(tickers),
            }
        )
    return dynamic + file_universes


def load_universe(name_or_path: str) -> list[str]:
    direct_path = Path(name_or_path)
    candidate = direct_path if direct_path.exists() else UNIVERSES_DIR / name_or_path

    if candidate.exists():
        return _read_universe_file(candidate)

    name = (name_or_path or "").lower()
    try:
        if name == "sp500":
            tickers = _ensure_list(yf.tickers_sp500())
            return tickers if tickers else FALLBACK_SP500
        if name == "nasdaq100":
            tickers = _ensure_list(yf.tickers_nasdaq())
            return tickers[:150] if tickers else FALLBACK_NASDAQ100
    except Exception:
        if name == "sp500":
            return FALLBACK_SP500
        if name == "nasdaq100":
            return FALLBACK_NASDAQ100

    raise UniverseNotFoundError(f"Unknown universe or missing file: {name_or_path}")
