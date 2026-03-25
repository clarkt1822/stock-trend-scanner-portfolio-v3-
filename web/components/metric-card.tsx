import { ArrowDownRight, ArrowUpRight, type LucideIcon } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export function MetricCard({
  label,
  value,
  hint,
  icon: Icon,
  tone = "neutral",
}: {
  label: string;
  value: string;
  hint: string;
  icon: LucideIcon;
  tone?: "neutral" | "positive" | "warning";
}) {
  const badgeClass =
    tone === "positive"
      ? "border-emerald-400/20 bg-emerald-400/10 text-emerald-200"
      : tone === "warning"
        ? "border-amber-400/20 bg-amber-400/10 text-amber-100"
        : "border-cyan-400/20 bg-cyan-400/10 text-cyan-100";

  return (
    <Card className="overflow-hidden">
      <CardHeader className="flex-row items-center justify-between space-y-0">
        <div>
          <p className="text-sm text-slate-400">{label}</p>
          <CardTitle className="mt-2 text-3xl">{value}</CardTitle>
        </div>
        <div className="rounded-2xl border border-white/10 bg-white/5 p-3 text-slate-100">
          <Icon className="h-5 w-5" />
        </div>
      </CardHeader>
      <CardContent className="flex items-center justify-between">
        <span className="text-sm text-slate-400">{hint}</span>
        <Badge className={badgeClass}>{tone === "warning" ? <ArrowDownRight className="mr-1 h-3.5 w-3.5" /> : <ArrowUpRight className="mr-1 h-3.5 w-3.5" />}Live terminal</Badge>
      </CardContent>
    </Card>
  );
}
