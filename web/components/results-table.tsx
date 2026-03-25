"use client";

import * as React from "react";
import {
  flexRender,
  getCoreRowModel,
  getFilteredRowModel,
  getSortedRowModel,
  type ColumnDef,
  type SortingState,
  useReactTable,
} from "@tanstack/react-table";
import { ArrowUpDown, Search } from "lucide-react";

import { Input } from "@/components/ui/input";
import type { ScanResultRow } from "@/types/scanner";

function formatNumber(value: number | null, digits = 2) {
  if (value === null || Number.isNaN(value)) {
    return "N/A";
  }
  return value.toLocaleString(undefined, { maximumFractionDigits: digits, minimumFractionDigits: digits });
}

export function ResultsTable({
  data,
  onSelect,
}: {
  data: ScanResultRow[];
  onSelect: (row: ScanResultRow) => void;
}) {
  const [sorting, setSorting] = React.useState<SortingState>([{ id: "score", desc: true }]);
  const [globalFilter, setGlobalFilter] = React.useState("");

  const columns = React.useMemo<ColumnDef<ScanResultRow>[]>(
    () => [
      {
        accessorKey: "ticker",
        header: "Ticker",
        cell: ({ row }) => <div className="font-semibold text-white">{row.original.ticker}</div>,
      },
      {
        accessorKey: "score",
        header: ({ column }) => (
          <button className="inline-flex items-center gap-2" onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}>
            Score
            <ArrowUpDown className="h-4 w-4 text-slate-500" />
          </button>
        ),
      },
      {
        accessorKey: "price",
        header: "Price",
        cell: ({ row }) => <span>${formatNumber(row.original.price)}</span>,
      },
      {
        accessorKey: "gap_pct",
        header: "Gap %",
        cell: ({ row }) => <span className={row.original.gap_pct !== null && row.original.gap_pct > 0 ? "text-emerald-300" : "text-slate-300"}>{formatNumber(row.original.gap_pct)}%</span>,
      },
      {
        accessorKey: "rel_dollar_vol",
        header: "Rel $Vol",
        cell: ({ row }) => <span>{formatNumber(row.original.rel_dollar_vol)}x</span>,
      },
      {
        accessorKey: "avg20_dollar_vol",
        header: "Avg $Vol",
        cell: ({ row }) => <span>${formatNumber(row.original.avg20_dollar_vol, 0)}</span>,
      },
      {
        id: "reasons",
        header: "Signals",
        accessorFn: (row) => row.reasons.join(", "),
        cell: ({ row }) => <span className="line-clamp-1 text-slate-400">{row.original.reasons.join("; ") || "No signal"}</span>,
      },
    ],
    [],
  );

  const table = useReactTable({
    data,
    columns,
    state: {
      sorting,
      globalFilter,
    },
    onSortingChange: setSorting,
    onGlobalFilterChange: setGlobalFilter,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    globalFilterFn: (row, _, filterValue) => {
      const term = String(filterValue).toLowerCase();
      return [row.original.ticker, row.original.reasons.join(" ")].join(" ").toLowerCase().includes(term);
    },
  });

  return (
    <div className="space-y-4">
      <div className="relative max-w-sm">
        <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-500" />
        <Input placeholder="Filter by ticker or signal..." className="pl-10" value={globalFilter} onChange={(event) => setGlobalFilter(event.target.value)} />
      </div>

      <div className="overflow-hidden rounded-3xl border border-white/10">
        <div className="overflow-x-auto">
          <table className="min-w-full border-collapse text-sm">
            <thead className="bg-white/5 text-left text-slate-400">
              {table.getHeaderGroups().map((headerGroup) => (
                <tr key={headerGroup.id}>
                  {headerGroup.headers.map((header) => (
                    <th key={header.id} className="px-4 py-4 font-medium">
                      {header.isPlaceholder ? null : flexRender(header.column.columnDef.header, header.getContext())}
                    </th>
                  ))}
                </tr>
              ))}
            </thead>
            <tbody>
              {table.getRowModel().rows.map((row) => (
                <tr
                  key={row.id}
                  className="cursor-pointer border-t border-white/5 bg-slate-950/20 text-slate-200 transition hover:bg-cyan-300/5"
                  onClick={() => onSelect(row.original)}
                >
                  {row.getVisibleCells().map((cell) => (
                    <td key={cell.id} className="px-4 py-4 align-top">
                      {flexRender(cell.column.columnDef.cell, cell.getContext())}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
