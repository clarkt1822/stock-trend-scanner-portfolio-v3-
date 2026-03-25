from __future__ import annotations

import io
from typing import Any

import pandas as pd

from api.scanner.config import load_config
from api.scanner.engine import run_scan
from api.scanner.universes import UniverseNotFoundError, list_universe_options, load_universe


class ScannerService:
    def __init__(self) -> None:
        self.cfg = load_config()

    def get_universes(self) -> list[dict[str, Any]]:
        return list_universe_options()

    def run_scan(self, universe: str, mode: str) -> dict[str, Any]:
        try:
            tickers = load_universe(universe)
        except UniverseNotFoundError:
            raise
        dataframe = run_scan(tickers, self.cfg, mode=mode)
        normalized = self._normalize_dataframe(dataframe)
        return {
            "universe": universe,
            "mode": mode,
            "row_count": len(normalized),
            "columns": list(normalized.columns),
            "results": normalized.to_dict(orient="records"),
        }

    def export_csv(self, universe: str, mode: str) -> bytes:
        payload = self.run_scan(universe, mode)
        dataframe = pd.DataFrame(payload["results"])
        if "reasons" in dataframe:
            dataframe["reasons"] = dataframe["reasons"].apply(lambda value: "; ".join(value) if isinstance(value, list) else value)
        buffer = io.StringIO()
        dataframe.to_csv(buffer, index=False)
        return buffer.getvalue().encode("utf-8")

    @staticmethod
    def _normalize_dataframe(dataframe: pd.DataFrame) -> pd.DataFrame:
        normalized = dataframe.copy()
        for column in ["gap_pct", "rel_dollar_vol", "avg20_dollar_vol", "price", "premarket_last"]:
            if column in normalized:
                normalized[column] = normalized[column].where(pd.notna(normalized[column]), None)
        return normalized


scanner_service = ScannerService()
