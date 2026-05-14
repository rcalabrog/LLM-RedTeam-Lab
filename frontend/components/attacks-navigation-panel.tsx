import { ClassificationBadge } from "@/components/classification-badge";
import { formatCategory, formatSeverity } from "@/lib/presenters";
import { AttackResultRow } from "@/types/ui";

interface AttacksNavigationPanelProps {
  rows: AttackResultRow[];
  selectedAttackId: string | null;
  onSelectAttack: (attackId: string) => void;
}

export function AttacksNavigationPanel({
  rows,
  selectedAttackId,
  onSelectAttack
}: AttacksNavigationPanelProps) {
  return (
    <section className="flex h-full min-h-0 flex-col rounded-2xl border border-slate-700/70 bg-slate-900/60 p-3 backdrop-blur">
      <header className="shrink-0 border-b border-slate-700/60 pb-2">
        <div className="flex items-start justify-between gap-3">
          <div>
            <h2 className="text-sm font-semibold uppercase tracking-[0.12em] text-slate-200">Attacks</h2>
            <p className="mt-1 text-xs text-slate-400">Select a result to inspect in detail.</p>
          </div>
          <span className="shrink-0 rounded-full bg-slate-800/80 px-2 py-1 text-[11px] text-cyan-200">
            {rows.length} rows
          </span>
        </div>
      </header>

      <div className="mt-3 min-h-0 flex-1 space-y-2 overflow-y-auto pr-1">
        {rows.length === 0 ? (
          <div className="flex min-h-40 items-center rounded-xl border border-slate-700/70 bg-slate-950/35 p-4 text-sm text-slate-300">
            No campaign results loaded yet. Run a campaign or select a saved campaign.
          </div>
        ) : (
          rows.map((row) => {
            const selected = selectedAttackId === row.attackId;
            return (
              <button
                key={row.attackId}
                type="button"
                onClick={() => onSelectAttack(row.attackId)}
                className={`w-full rounded-xl border p-3 text-left transition ${
                  selected
                    ? "border-cyan-300/80 bg-cyan-500/15 ring-1 ring-cyan-300/35"
                    : "border-slate-700/70 bg-slate-900/55 hover:border-slate-500 hover:bg-slate-800/60"
                }`}
              >
                <div className="flex items-start justify-between gap-2">
                  <div className="min-w-0">
                    <p className="truncate font-mono text-xs font-semibold text-cyan-200">{row.attackId}</p>
                    <p className="mt-0.5 line-clamp-2 text-xs text-slate-300">{row.attackName}</p>
                  </div>
                  <ClassificationBadge classification={row.classification} />
                </div>

                <div className="mt-2 flex flex-wrap gap-1.5 text-[10px]">
                  <span className="rounded-full bg-slate-800/80 px-2 py-0.5 text-slate-300">
                    {formatCategory(row.category)}
                  </span>
                  <span className="rounded-full bg-slate-800/80 px-2 py-0.5 text-slate-300">
                    {formatSeverity(row.severity)}
                  </span>
                  <span className="rounded-full bg-slate-800/80 px-2 py-0.5 text-slate-300">
                    {row.executionStatus}
                  </span>
                </div>

                <div className="mt-2 flex gap-1.5 text-[11px]">
                  <span className="rounded-full bg-amber-500/15 px-2 py-0.5 text-amber-200">
                    W:{row.warningsCount}
                  </span>
                  <span className="rounded-full bg-rose-500/15 px-2 py-0.5 text-rose-200">
                    F:{row.flagsCount}
                  </span>
                </div>
              </button>
            );
          })
        )}
      </div>
    </section>
  );
}
