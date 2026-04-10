import { motion } from "framer-motion";

import { CampaignViewModel } from "@/types/ui";
import { formatCategory, formatRate, formatSeverity } from "@/lib/presenters";

interface MetricsPanelProps {
  view: CampaignViewModel | null;
}

export function MetricsPanel({ view }: MetricsPanelProps) {
  if (!view) {
    return (
      <section className="rounded-2xl border border-slate-700/70 bg-slate-900/60 p-4 backdrop-blur">
        <h3 className="text-sm font-semibold uppercase tracking-[0.12em] text-slate-200">Metrics</h3>
        <p className="mt-3 text-sm text-slate-300">Run a campaign to view aggregate evaluation metrics.</p>
      </section>
    );
  }

  const summary = view.evaluated.summary;
  const cards = [
    { label: "Offensive Success", value: summary.success_count, tone: "text-rose-200" },
    { label: "Defended / Failed", value: summary.failed_count, tone: "text-emerald-200" },
    { label: "Ambiguous", value: summary.ambiguous_count, tone: "text-amber-200" }
  ];

  return (
    <section className="space-y-4 rounded-2xl border border-slate-700/70 bg-slate-900/60 p-4 backdrop-blur">
      <div>
        <h3 className="text-sm font-semibold uppercase tracking-[0.12em] text-slate-200">Aggregate Metrics</h3>
        <p className="mt-1 text-xs text-slate-400">Summary for {view.evaluated.campaign_name}</p>
      </div>

      <div className="grid gap-2">
        {cards.map((card, index) => (
          <motion.div
            key={card.label}
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.25, delay: index * 0.06 }}
            className="rounded-xl border border-slate-700/70 bg-slate-900/60 p-3"
          >
            <p className="text-xs uppercase tracking-[0.12em] text-slate-400">{card.label}</p>
            <p className={`mt-1 text-2xl font-semibold ${card.tone}`}>{card.value}</p>
          </motion.div>
        ))}
      </div>

      <div className="rounded-xl border border-slate-700/70 bg-slate-900/60 p-3">
        <p className="text-xs uppercase tracking-[0.12em] text-slate-400">Rates</p>
        <div className="mt-2 space-y-1 text-sm text-slate-200">
          <p>Success: {formatRate(summary.success_rate_overall)}</p>
          <p>Failed: {formatRate(summary.failed_rate_overall)}</p>
          <p>Ambiguous: {formatRate(summary.ambiguous_rate_overall)}</p>
        </div>
      </div>

      <div className="rounded-xl border border-slate-700/70 bg-slate-900/60 p-3">
        <p className="text-xs uppercase tracking-[0.12em] text-slate-400">Category Breakdown</p>
        <div className="mt-2 space-y-2 text-sm">
          {summary.per_category.map((item) => (
            <div key={item.category} className="rounded-lg bg-slate-800/55 px-2 py-2">
              <div className="flex items-center justify-between">
                <span className="text-slate-200">{formatCategory(item.category)}</span>
                <span className="text-slate-400">{formatRate(item.success_rate)}</span>
              </div>
              <p className="mt-1 text-xs text-slate-400">
                S:{item.success} F:{item.failed} A:{item.ambiguous} / {item.total}
              </p>
            </div>
          ))}
        </div>
      </div>

      <div className="rounded-xl border border-slate-700/70 bg-slate-900/60 p-3">
        <p className="text-xs uppercase tracking-[0.12em] text-slate-400">Severity Breakdown</p>
        <div className="mt-2 space-y-1 text-xs text-slate-300">
          {summary.per_severity.map((item) => (
            <p key={item.severity}>
              {formatSeverity(item.severity)}: {item.success}/{item.total} success
            </p>
          ))}
        </div>
      </div>
    </section>
  );
}
