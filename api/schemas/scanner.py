from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class UniverseOption(BaseModel):
    id: str
    label: str
    kind: str
    count: int | None = None


class ScanRequest(BaseModel):
    universe: str = Field(default="demo_sample.csv")
    mode: Literal["live", "sample"] = "sample"


class ScanResultRow(BaseModel):
    ticker: str
    score: int
    gap_pct: float | None = None
    rel_dollar_vol: float | None = None
    avg20_dollar_vol: float | None = None
    price: float | None = None
    premarket_last: float | None = None
    reasons: list[str] = Field(default_factory=list)


class ScanResponse(BaseModel):
    universe: str
    mode: str
    row_count: int
    columns: list[str]
    results: list[ScanResultRow]


class HealthResponse(BaseModel):
    status: str
    app: str
