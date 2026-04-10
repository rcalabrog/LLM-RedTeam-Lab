import { durationBetweenIso, formatDateTime, formatDurationMs } from "@/lib/presenters";
import { CampaignViewModel, CenterWorkspaceMode } from "@/types/ui";

interface CampaignSummaryProps {
  view: CampaignViewModel | null;
  mode?: CenterWorkspaceMode;
  embedded?: boolean;
}

export function CampaignSummary({ view, mode = "setup", embedded = false }: CampaignSummaryProps) {
  const isResultsMode = mode === "results";

  if (!view) {
    return (
      <div className={`${embedded ? "" : "shrink-0 rounded-xl border border-slate-700/70 bg-slate-900/60"} text-slate-300 ${isResultsMode ? "p-2.5 text-xs" : "p-4 text-sm"}`}>
        <p className="text-[11px] uppercase tracking-[0.14em] text-slate-400">Current Campaign</p>
        <p className={isResultsMode ? "mt-1" : "mt-2"}>
          No campaign loaded yet. Configure a target and execute a run to inspect results.
        </p>
      </div>
    );
  }

  const durationMs = durationBetweenIso(view.evaluated.source_started_at, view.evaluated.source_completed_at);

  return (
    <div className={`${embedded ? "" : "shrink-0 rounded-xl border border-slate-700/70 bg-slate-900/60"} ${isResultsMode ? "p-2.5" : "p-4"}`}>
      <div
        className={`flex flex-wrap items-center justify-between gap-2 border-b border-slate-700/60 text-xs text-slate-400 ${
          isResultsMode ? "pb-1.5" : "pb-2"
        }`}
      >
        <p className="text-[11px] uppercase tracking-[0.14em] text-cyan-300">Current Campaign</p>
        <div className="flex flex-wrap items-center gap-2">
          <span className="rounded-full bg-slate-800/70 px-2 py-1">{view.source}</span>
          {view.savedAt && <span>saved: {formatDateTime(view.savedAt)}</span>}
        </div>
      </div>
      <div className={`flex flex-wrap items-center gap-2 text-xs text-slate-400 ${isResultsMode ? "mt-1" : "mt-2"}`}>
        <span>run_id: {view.evaluated.run_id}</span>
      </div>
      <h3 className={`font-semibold text-slate-100 ${isResultsMode ? "mt-1 text-base" : "mt-2 text-lg"}`}>
        {view.evaluated.campaign_name}
      </h3>
      <p className={`text-slate-300 ${isResultsMode ? "mt-0.5 text-xs" : "mt-1 text-sm"}`}>
        Target: <span className="text-slate-100">{view.evaluated.target_name}</span> | Evaluated at{" "}
        {formatDateTime(view.evaluated.evaluated_at)}
      </p>
      <p className={`text-slate-300 ${isResultsMode ? "mt-0.5 text-xs" : "mt-1 text-sm"}`}>
        Execution time:{" "}
        <span className="font-semibold text-cyan-200">
          {durationMs === null ? "n/a" : formatDurationMs(durationMs)}
        </span>
      </p>
    </div>
  );
}
