export type ScanMode = "live" | "sample";

export interface UniverseOption {
  id: string;
  label: string;
  kind: string;
  count?: number;
}

export interface ScanResultRow {
  ticker: string;
  score: number;
  gap_pct: number | null;
  rel_dollar_vol: number | null;
  avg20_dollar_vol: number | null;
  price: number | null;
  premarket_last: number | null;
  reasons: string[];
}

export interface ScanResponse {
  universe: string;
  mode: ScanMode;
  row_count: number;
  columns: string[];
  results: ScanResultRow[];
}
