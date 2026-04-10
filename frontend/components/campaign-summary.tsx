import { durationBetweenIso, formatDateTime, formatDurationMs } from "@/lib/presenters";
import { CampaignViewModel } from "@/types/ui";

interface CampaignSummaryProps {
  view: CampaignViewModel | null;
}

export function CampaignSummary({ view }: CampaignSummaryProps) {
  if (!view) {
    return (
      <div className="rounded-xl border border-slate-700/70 bg-slate-900/60 p-4 text-sm text-slate-300">
        No campaign loaded yet. Configure a target and execute a run to inspect results.
      </div>
    );
  }

  const durationMs = durationBetweenIso(view.evaluated.source_started_at, view.evaluated.source_completed_at);

  return (
    <div className="rounded-xl border border-slate-700/70 bg-slate-900/60 p-4">
      <div className="flex flex-wrap items-center gap-2 text-xs text-slate-400">
        <span className="rounded-full bg-slate-800/70 px-2 py-1">{view.source}</span>
        <span>run_id: {view.evaluated.run_id}</span>
        {view.savedAt && <span>saved: {formatDateTime(view.savedAt)}</span>}
      </div>
      <h3 className="mt-2 text-lg font-semibold text-slate-100">{view.evaluated.campaign_name}</h3>
      <p className="mt-1 text-sm text-slate-300">
        Target: <span className="text-slate-100">{view.evaluated.target_name}</span> | Evaluated at{" "}
        {formatDateTime(view.evaluated.evaluated_at)}
      </p>
      <p className="mt-1 text-sm text-slate-300">
        Execution time:{" "}
        <span className="font-semibold text-cyan-200">
          {durationMs === null ? "n/a" : formatDurationMs(durationMs)}
        </span>
      </p>
    </div>
  );
}
