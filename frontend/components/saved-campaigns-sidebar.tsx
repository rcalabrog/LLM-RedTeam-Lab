import { motion } from "framer-motion";

import { SavedCampaignSummary } from "@/types/api";
import { formatDateTime, formatRate } from "@/lib/presenters";
import { ReadinessIndicator } from "@/components/readiness-indicator";
import { ReadinessResponse } from "@/types/api";

interface SavedCampaignsSidebarProps {
  campaigns: SavedCampaignSummary[];
  selectedRunId: string | null;
  loading: boolean;
  error: string | null;
  readiness: ReadinessResponse | null;
  readinessLoading: boolean;
  onSelectCampaign: (runId: string) => void;
  onNewRun: () => void;
}

export function SavedCampaignsSidebar({
  campaigns,
  selectedRunId,
  loading,
  error,
  readiness,
  readinessLoading,
  onSelectCampaign,
  onNewRun
}: SavedCampaignsSidebarProps) {
  return (
    <aside className="flex h-full min-h-0 flex-col rounded-2xl border border-slate-700/70 bg-slate-900/60 p-4 backdrop-blur">
      <div className="shrink-0 flex items-center justify-between gap-2">
        <h2 className="text-sm font-semibold uppercase tracking-[0.12em] text-slate-200">Saved Campaigns</h2>
        <button
          type="button"
          onClick={onNewRun}
          className="rounded-lg bg-cyan-400/20 px-3 py-1.5 text-xs font-semibold text-cyan-100 ring-1 ring-cyan-300/40 transition hover:bg-cyan-400/30"
        >
          New Run
        </button>
      </div>

      <div className="mt-4 shrink-0">
        <ReadinessIndicator readiness={readiness} loading={readinessLoading} />
      </div>

      <div className="mt-4 min-h-0 flex-1 space-y-2 overflow-y-auto pr-1">
        {loading && <p className="rounded-lg bg-slate-900/60 p-3 text-xs text-slate-300">Loading campaigns...</p>}

        {error && <p className="rounded-lg bg-rose-500/10 p-3 text-xs text-rose-200">{error}</p>}

        {!loading && !error && campaigns.length === 0 && (
          <p className="rounded-lg bg-slate-900/60 p-3 text-xs text-slate-300">
            No saved campaigns yet. Run and save a campaign to build your history.
          </p>
        )}

        {campaigns.map((campaign) => {
          const selected = selectedRunId === campaign.run_id;
          return (
            <motion.button
              key={campaign.run_id}
              type="button"
              whileHover={{ y: -1 }}
              onClick={() => onSelectCampaign(campaign.run_id)}
              className={`w-full rounded-xl border p-3 text-left transition ${
                selected
                  ? "border-cyan-300/80 bg-cyan-500/15 ring-1 ring-cyan-300/35"
                  : "border-slate-700/70 bg-slate-900/55 hover:border-slate-500 hover:bg-slate-800/60"
              }`}
            >
              <p className="truncate text-sm font-semibold text-slate-100">{campaign.campaign_name}</p>
              <p className="mt-0.5 text-xs text-slate-400">
                {campaign.target_name} • {campaign.pipeline_state}
              </p>
              <div className="mt-2 flex flex-wrap gap-1.5 text-[10px]">
                <span className="rounded-full bg-slate-800/80 px-2 py-0.5 text-emerald-300">
                  F:{campaign.failed_count}
                </span>
                <span className="rounded-full bg-slate-800/80 px-2 py-0.5 text-rose-300">
                  S:{campaign.success_count}
                </span>
                <span className="rounded-full bg-slate-800/80 px-2 py-0.5 text-amber-300">
                  A:{campaign.ambiguous_count}
                </span>
              </div>
              <div className="mt-2 flex items-center justify-between text-[11px] text-slate-400">
                <span>{formatDateTime(campaign.completed_at)}</span>
                <span>{formatRate(campaign.success_rate_overall)} resisted</span>
              </div>
            </motion.button>
          );
        })}
      </div>
    </aside>
  );
}
