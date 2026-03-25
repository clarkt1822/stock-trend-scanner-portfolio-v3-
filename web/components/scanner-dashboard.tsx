"use client";

import * as React from "react";
import { Activity, BarChart3, Download, Radar, RefreshCcw, Sparkles } from "lucide-react";

import { DetailPanel } from "@/components/detail-panel";
import { MetricCard } from "@/components/metric-card";
import { ResultsTable } from "@/components/results-table";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { fetchUniverses, exportScan, runScan } from "@/lib/api";
import { cn } from "@/lib/utils";
import type { ScanMode, ScanResponse, ScanResultRow, UniverseOption } from "@/types/scanner";

function formatCompactCurrency(value: number) {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    notation: "compact",
    maximumFractionDigits: 1,
  }).format(value);
}

export function ScannerDashboard() {
  const [universes, setUniverses] = React.useState<UniverseOption[]>([]);
  const [selectedUniverse, setSelectedUniverse] = React.useState("demo_sample.csv");
  const [mode, setMode] = React.useState<ScanMode>("sample");
  const [scanData, setScanData] = React.useState<ScanResponse | null>(null);
  const [selectedRow, setSelectedRow] = React.useState<ScanResultRow | null>(null);
  const [loading, setLoading] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);
  const [exporting, setExporting] = React.useState(false);
  const controlsDisabled = loading || universes.length === 0;

  React.useEffect(() => {
    async function loadUniverses() {
      try {
        const items = await fetchUniverses();
        setUniverses(items);
        const preferred = items.find((item) => item.id === "demo_sample.csv");
        if (preferred) {
          setSelectedUniverse(preferred.id);
        } else if (items.length > 0) {
          setSelectedUniverse(items[0].id);
        }
      } catch (cause) {
        setError(cause instanceof Error ? cause.message : "Failed to load universes.");
      }
    }

    loadUniverses();
  }, []);

  async function handleRunScan() {
    setLoading(true);
    setError(null);
    setSelectedRow(null);
    try {
      const result = await runScan(selectedUniverse, mode);
      setScanData(result);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Scan failed.");
      setScanData(null);
    } finally {
      setLoading(false);
    }
  }

  async function handleExport() {
    setExporting(true);
    setError(null);
    try {
      const blob = await exportScan(selectedUniverse, mode);
      const url = URL.createObjectURL(blob);
      const anchor = document.createElement("a");
      anchor.href = url;
      anchor.download = `scanner-results-${selectedUniverse}-${mode}.csv`;
      anchor.click();
      URL.revokeObjectURL(url);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "CSV export failed.");
    } finally {
      setExporting(false);
    }
  }

  const resultRows = scanData?.results ?? [];
  const positiveSignals = resultRows.filter((row) => row.score > 0).length;
  const topScore = resultRows[0]?.score ?? 0;
  const highestLiquidity = resultRows.reduce((max, row) => Math.max(max, row.avg20_dollar_vol ?? 0), 0);

  return (
    <main className="relative min-h-screen overflow-hidden px-4 py-6 sm:px-6 lg:px-10">
      <div className="mx-auto flex max-w-7xl flex-col gap-6">
        <section className="grid gap-6 lg:grid-cols-[1.4fr_0.9fr]">
          <Card className="overflow-hidden border-cyan-400/20 shadow-glow">
            <CardContent className="relative p-0">
              <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_left,rgba(45,212,191,0.18),transparent_32%),radial-gradient(circle_at_80%_20%,rgba(37,99,235,0.18),transparent_26%)]" />
              <div className="relative p-7">
                <div className="flex flex-wrap items-center gap-3">
                  <span className="rounded-full border border-cyan-300/20 bg-cyan-300/10 px-3 py-1 text-xs uppercase tracking-[0.28em] text-cyan-100">
                    Portfolio scanner
                  </span>
                  <span className="text-xs uppercase tracking-[0.28em] text-slate-500">FastAPI + Next.js</span>
                </div>
                <div className="mt-6 max-w-2xl">
                  <h1 className="text-4xl font-semibold tracking-tight text-white sm:text-5xl">Stock Trend Scanner</h1>
                  <p className="mt-4 text-base leading-7 text-slate-300">
                    A web-first rebuild of a legacy Python stock scanner. Preserve the signal engine, sharpen the interface, and surface ranked setups in a clean terminal-style dashboard.
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Scan Controls</CardTitle>
              <CardDescription>Choose a universe, pick a data mode, and run the existing Python engine through the API.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-5">
              <div className="grid gap-4 sm:grid-cols-2">
                <label className="space-y-2 text-sm text-slate-300">
                  <span>Universe</span>
                  <select
                    className="h-11 w-full rounded-xl border border-white/10 bg-white/5 px-3 text-slate-100 outline-none"
                    value={selectedUniverse}
                    onChange={(event) => setSelectedUniverse(event.target.value)}
                  >
                    {universes.map((universe) => (
                      <option key={universe.id} value={universe.id}>
                        {universe.label}
                      </option>
                    ))}
                  </select>
                </label>

                <label className="space-y-2 text-sm text-slate-300">
                  <span>Mode</span>
                  <select className="h-11 w-full rounded-xl border border-white/10 bg-white/5 px-3 text-slate-100 outline-none" value={mode} onChange={(event) => setMode(event.target.value as ScanMode)}>
                    <option value="sample">Sample data</option>
                    <option value="live">Live yfinance</option>
                  </select>
                </label>
              </div>

              <div className="flex flex-wrap gap-3">
                <Button onClick={handleRunScan} disabled={controlsDisabled}>
                  <Radar className="h-4 w-4" />
                  {loading ? "Running scan..." : "Run Scan"}
                </Button>
                <Button variant="secondary" onClick={handleExport} disabled={exporting || resultRows.length === 0}>
                  <Download className="h-4 w-4" />
                  {exporting ? "Exporting..." : "Export CSV"}
                </Button>
                <Button variant="ghost" onClick={handleRunScan} disabled={controlsDisabled}>
                  <RefreshCcw className="h-4 w-4" />
                  Refresh
                </Button>
              </div>

              <div className="rounded-2xl border border-white/10 bg-slate-950/30 p-4 text-sm text-slate-400">
                <p className="font-medium text-slate-200">Current configuration</p>
                <p className="mt-2">Universe: <span className="text-slate-100">{selectedUniverse}</span></p>
                <p className="mt-1">Data mode: <span className="text-slate-100">{mode}</span></p>
              </div>
            </CardContent>
          </Card>
        </section>

        <section className="grid gap-4 md:grid-cols-3">
          <MetricCard label="Matched symbols" value={String(resultRows.length)} hint="Rows returned by current scan" icon={Activity} />
          <MetricCard label="Positive setups" value={String(positiveSignals)} hint="Signals with a score above zero" icon={Sparkles} tone="positive" />
          <MetricCard label="Liquidity ceiling" value={highestLiquidity ? formatCompactCurrency(highestLiquidity) : "$0"} hint={`Top score ${topScore}`} icon={BarChart3} tone="warning" />
        </section>

        <Card>
          <CardHeader className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
            <div>
              <CardTitle>Scan Results</CardTitle>
              <CardDescription>Sortable, filterable results powered by TanStack Table. Click a row to inspect signal details.</CardDescription>
            </div>
            <div className="text-sm text-slate-500">
              {scanData ? `Universe ${scanData.universe} | ${scanData.mode} mode | ${scanData.row_count} rows` : "No scan has been run yet."}
            </div>
          </CardHeader>
          <CardContent>
            {loading ? (
              <div className="rounded-3xl border border-dashed border-white/10 bg-white/[0.03] px-6 py-16 text-center">
                <div className="mx-auto h-10 w-10 animate-spin rounded-full border-2 border-cyan-300/20 border-t-cyan-300" />
                <p className="mt-4 text-lg font-medium text-slate-100">Crunching the watchlist</p>
                <p className="mt-2 text-sm text-slate-500">Fetching price history, premarket data, and candlestick signals.</p>
              </div>
            ) : error ? (
              <div className="rounded-3xl border border-rose-400/20 bg-rose-500/10 px-6 py-12 text-center">
                <p className="text-lg font-medium text-rose-100">Scanner error</p>
                <p className="mt-2 text-sm text-rose-200/80">{error}</p>
              </div>
            ) : !scanData ? (
              <div className="rounded-3xl border border-dashed border-white/10 bg-white/[0.03] px-6 py-16 text-center">
                <p className="text-lg font-medium text-slate-100">No scan loaded</p>
                <p className="mt-2 text-sm text-slate-500">Run the scanner to populate the dashboard and enable CSV export.</p>
              </div>
            ) : resultRows.length === 0 ? (
              <div className="rounded-3xl border border-dashed border-white/10 bg-white/[0.03] px-6 py-16 text-center">
                <p className="text-lg font-medium text-slate-100">No symbols matched</p>
                <p className="mt-2 text-sm text-slate-500">Try a different universe or switch to sample mode to demo the interface offline.</p>
              </div>
            ) : (
              <ResultsTable data={resultRows} onSelect={setSelectedRow} />
            )}
          </CardContent>
        </Card>
      </div>

      <div className={cn("fixed inset-0 z-20 bg-black/40 transition", selectedRow ? "pointer-events-auto opacity-100" : "pointer-events-none opacity-0")} onClick={() => setSelectedRow(null)} />
      <DetailPanel row={selectedRow} onClose={() => setSelectedRow(null)} />
    </main>
  );
}
