"use client";

import { X } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import type { ScanResultRow } from "@/types/scanner";

function formatNumber(value: number | null, digits = 2) {
  if (value === null || Number.isNaN(value)) {
    return "N/A";
  }
  return value.toLocaleString(undefined, { maximumFractionDigits: digits, minimumFractionDigits: digits });
}

export function DetailPanel({
  row,
  onClose,
}: {
  row: ScanResultRow | null;
  onClose: () => void;
}) {
  return (
    <div
      className={`fixed inset-y-0 right-0 z-30 w-full max-w-md transform border-l border-white/10 bg-slate-950/95 p-6 shadow-2xl shadow-black/50 backdrop-blur-xl transition ${row ? "translate-x-0" : "translate-x-full"}`}
    >
      <div className="flex items-center justify-between">
        <div>
          <p className="text-xs uppercase tracking-[0.3em] text-cyan-300/70">Ticker detail</p>
          <h2 className="mt-2 text-3xl font-semibold text-white">{row?.ticker ?? "--"}</h2>
        </div>
        <Button variant="ghost" size="sm" onClick={onClose}>
          <X className="h-4 w-4" />
        </Button>
      </div>

      {row ? (
        <div className="mt-6 space-y-4">
          <Card className="p-5">
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <p className="text-slate-500">Score</p>
                <p className="mt-1 text-xl font-semibold text-white">{row.score}</p>
              </div>
              <div>
                <p className="text-slate-500">Last price</p>
                <p className="mt-1 text-xl font-semibold text-white">${formatNumber(row.price)}</p>
              </div>
              <div>
                <p className="text-slate-500">Gap %</p>
                <p className="mt-1 text-xl font-semibold text-white">{formatNumber(row.gap_pct)}%</p>
              </div>
              <div>
                <p className="text-slate-500">Rel $Vol</p>
                <p className="mt-1 text-xl font-semibold text-white">{formatNumber(row.rel_dollar_vol)}x</p>
              </div>
            </div>
          </Card>

          <Card className="p-5">
            <p className="text-sm font-medium text-slate-200">Triggered rules</p>
            <div className="mt-4 flex flex-wrap gap-2">
              {row.reasons.length > 0 ? row.reasons.map((reason) => <Badge key={reason} className="bg-white/5">{reason}</Badge>) : <span className="text-sm text-slate-500">No positive signals recorded.</span>}
            </div>
          </Card>
        </div>
      ) : null}
    </div>
  );
}
