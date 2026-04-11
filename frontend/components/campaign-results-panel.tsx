import { AttackResultsTable } from "@/components/attack-results-table";
import { AttackResultRow, CenterWorkspaceMode } from "@/types/ui";

interface CampaignResultsPanelProps {
  rows: AttackResultRow[];
  selectedAttackId: string | null;
  mode?: CenterWorkspaceMode;
  embedded?: boolean;
  onSelectRow: (attackId: string) => void;
}

export function CampaignResultsPanel({
  rows,
  selectedAttackId,
  mode = "setup",
  embedded = false,
  onSelectRow
}: CampaignResultsPanelProps) {
  const isResultsMode = mode === "results";

  return (
    <section
      className={`isolate flex h-full min-h-0 flex-1 flex-col overflow-hidden ${
        embedded
          ? "rounded-lg border border-slate-700/70 bg-slate-900/55"
          : "rounded-2xl border border-slate-700/70 bg-slate-900/60 backdrop-blur"
      } ${isResultsMode ? "p-3.5" : "p-3"}`}
    >
      {!embedded && (
        <header className="shrink-0 border-b border-slate-700/60 pb-2">
          <div className="flex flex-wrap items-center justify-between gap-2">
            <h3 className="text-sm font-semibold uppercase tracking-[0.12em] text-slate-200">Campaign Results</h3>
            <div className="flex items-center gap-1.5 text-[11px] text-slate-400">
              <span className="rounded-full bg-slate-800/70 px-2 py-1">{rows.length} rows</span>
              <span className="rounded-full bg-slate-800/70 px-2 py-1">
                {selectedAttackId ? `selected: ${selectedAttackId}` : "select a row"}
              </span>
            </div>
          </div>
          <p className="mt-1 text-xs text-slate-400">
            Grid view of per-attack execution and deterministic evaluation.
          </p>
        </header>
      )}

      <div
        className={`h-full min-h-0 flex-1 overflow-hidden ${embedded ? "" : isResultsMode ? "mt-2.5" : "mt-3"}`}
      >
        <AttackResultsTable rows={rows} selectedAttackId={selectedAttackId} onSelectRow={onSelectRow} />
      </div>
    </section>
  );
}
