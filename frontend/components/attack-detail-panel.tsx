import { ClassificationBadge } from "@/components/classification-badge";
import { formatCategory, formatSeverity } from "@/lib/presenters";
import { AttackResultRow } from "@/types/ui";

interface AttackDetailPanelProps {
  row: AttackResultRow | null;
}

function stringifyMetadata(value: unknown): string {
  if (value == null) {
    return "n/a";
  }
  try {
    return JSON.stringify(value, null, 2);
  } catch {
    return String(value);
  }
}

export function AttackDetailPanel({ row }: AttackDetailPanelProps) {
  if (!row) {
    return (
      <section className="rounded-2xl border border-slate-700/70 bg-slate-900/60 p-4 backdrop-blur">
        <h3 className="text-sm font-semibold uppercase tracking-[0.12em] text-slate-200">Attack Detail</h3>
        <p className="mt-3 text-sm text-slate-300">Select an attack result row to inspect evaluation evidence.</p>
      </section>
    );
  }

  return (
    <section className="space-y-4 rounded-2xl border border-slate-700/70 bg-slate-900/60 p-4 backdrop-blur">
      <div>
        <p className="text-xs uppercase tracking-[0.12em] text-slate-400">{row.attackId}</p>
        <h3 className="mt-1 text-lg font-semibold text-slate-100">{row.attackName}</h3>
      </div>

      <div className="flex items-center gap-2">
        <ClassificationBadge classification={row.classification} />
        <span className="rounded-full bg-slate-800/70 px-2 py-1 text-xs text-slate-300">
          {formatCategory(row.category)}
        </span>
        <span className="rounded-full bg-slate-800/70 px-2 py-1 text-xs text-slate-300">
          {formatSeverity(row.severity)}
        </span>
      </div>

      <div className="rounded-xl border border-slate-700/70 bg-slate-900/60 p-3">
        <p className="text-xs uppercase tracking-[0.12em] text-slate-400">Reasoning Summary</p>
        <p className="mt-2 text-sm text-slate-200">{row.reasoningSummary}</p>
      </div>

      <div className="rounded-xl border border-slate-700/70 bg-slate-900/60 p-3">
        <p className="text-xs uppercase tracking-[0.12em] text-slate-400">Matched Signals</p>
        <div className="mt-2 flex flex-wrap gap-2">
          {row.matchedSignals.length === 0 && <span className="text-sm text-slate-400">None</span>}
          {row.matchedSignals.map((signal) => (
            <span key={signal} className="rounded-full bg-slate-800/80 px-2 py-1 text-xs text-slate-200">
              {signal}
            </span>
          ))}
        </div>
      </div>

      <div className="rounded-xl border border-slate-700/70 bg-slate-900/60 p-3">
        <p className="text-xs uppercase tracking-[0.12em] text-slate-400">Matched Rules</p>
        <div className="mt-2 space-y-2">
          {row.matchedRules.length === 0 && <p className="text-sm text-slate-400">None</p>}
          {row.matchedRules.map((rule) => (
            <div key={rule.rule_id} className="rounded-lg bg-slate-800/60 p-2">
              <p className="text-xs font-semibold text-slate-200">{rule.rule_id}</p>
              <p className="mt-1 text-xs text-slate-400">{rule.evidence}</p>
            </div>
          ))}
        </div>
      </div>

      <div className="rounded-xl border border-slate-700/70 bg-slate-900/60 p-3">
        <p className="text-xs uppercase tracking-[0.12em] text-slate-400">Response Excerpt</p>
        <p className="mt-2 text-sm text-slate-200">{row.responseExcerpt ?? "No excerpt available."}</p>
      </div>

      <div className="rounded-xl border border-slate-700/70 bg-slate-900/60 p-3">
        <p className="text-xs uppercase tracking-[0.12em] text-slate-400">Execution Snapshot</p>
        <div className="mt-2 text-xs text-slate-300">
          <p>Execution status: {row.executionStatus}</p>
          <p>Warnings: {row.warningsCount}</p>
          <p>Flags: {row.flagsCount}</p>
          <p>Defense mode: {row.rawResult?.defense_mode ?? "n/a"}</p>
          <p>Risk level: {row.rawResult?.execution_metadata.risk_level ?? "n/a"}</p>
        </div>
        <pre className="mt-2 max-h-40 overflow-auto rounded-lg bg-slate-950/70 p-2 text-[11px] text-slate-300">
          {stringifyMetadata(row.rawResult?.execution_metadata.raw_target_metadata)}
        </pre>
      </div>
    </section>
  );
}
