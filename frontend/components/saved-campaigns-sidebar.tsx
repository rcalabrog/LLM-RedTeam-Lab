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
    <aside className="rounded-2xl border border-slate-700/70 bg-slate-900/60 p-4 backdrop-blur">
      <div className="flex items-center justify-between gap-2">
        <h2 className="text-sm font-semibold uppercase tracking-[0.12em] text-slate-200">Saved Campaigns</h2>
        <button
          type="button"
          onClick={onNewRun}
          className="rounded-lg bg-cyan-400/20 px-3 py-1.5 text-xs font-semibold text-cyan-100 ring-1 ring-cyan-300/40 transition hover:bg-cyan-400/30"
        >
          New Run
        </button>
      </div>

      <div className="mt-4">
        <ReadinessIndicator readiness={readiness} loading={readinessLoading} />
      </div>

      <div className="mt-4 max-h-[56vh] space-y-2 overflow-y-auto pr-1">
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
                  ? "border-cyan-300/70 bg-cyan-500/15"
                  : "border-slate-700/70 bg-slate-900/55 hover:border-slate-600"
              }`}
            >
              <p className="truncate text-sm font-semibold text-slate-100">{campaign.campaign_name}</p>
              <p className="mt-0.5 text-xs text-slate-400">{campaign.target_name}</p>
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
