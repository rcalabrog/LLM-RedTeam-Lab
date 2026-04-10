import { AttackCategory, AttackSeverity, WorkflowCatalogResponse } from "@/types/api";
import { CampaignFormState } from "@/types/ui";
import { formatCategory, formatDurationMs, formatSeverity } from "@/lib/presenters";
import { motion } from "framer-motion";

const categories: AttackCategory[] = [
  "jailbreak_basic",
  "prompt_injection_direct",
  "system_prompt_extraction",
  "policy_bypass",
  "data_leakage_simulation"
];

const severities: AttackSeverity[] = ["low", "medium", "high"];

interface CampaignConfiguratorProps {
  catalog: WorkflowCatalogResponse | null;
  loading: boolean;
  formState: CampaignFormState;
  running: boolean;
  runElapsedMs: number;
  runError: string | null;
  onChange: (patch: Partial<CampaignFormState>) => void;
  onApplyVulnerablePreset: () => void;
  onApplyGuardedDefaultPreset: () => void;
  onRun: () => void;
  onRunEvaluateOnly: () => void;
}

export function CampaignConfigurator({
  catalog,
  loading,
  formState,
  running,
  runElapsedMs,
  runError,
  onChange,
  onApplyVulnerablePreset,
  onApplyGuardedDefaultPreset,
  onRun,
  onRunEvaluateOnly
}: CampaignConfiguratorProps) {
  const defensesEnabled = formState.targetName === "guarded_chat";

  return (
    <section className="rounded-2xl border border-slate-700/70 bg-slate-900/60 p-4 backdrop-blur">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h2 className="text-lg font-semibold text-slate-100">Campaign Configuration</h2>
          <p className="mt-1 text-sm text-slate-300">
            Configure one attack batch and run deterministic evaluation for vulnerable vs defended targets.
          </p>
        </div>
        <div className="flex gap-2">
          <button
            type="button"
            onClick={onApplyVulnerablePreset}
            className="rounded-lg border border-slate-600 px-3 py-1.5 text-xs font-semibold text-slate-200 transition hover:border-slate-400"
          >
            Vulnerable Baseline
          </button>
          <button
            type="button"
            onClick={onApplyGuardedDefaultPreset}
            className="rounded-lg border border-cyan-400/50 px-3 py-1.5 text-xs font-semibold text-cyan-200 transition hover:bg-cyan-500/10"
          >
            Guarded Default
          </button>
        </div>
      </div>

      {loading && <p className="mt-4 text-sm text-slate-300">Loading catalog configuration...</p>}

      {!loading && catalog && (
        <div className="mt-4 grid grid-cols-2 gap-3">
          <label className="space-y-1">
            <span className="text-xs uppercase tracking-[0.12em] text-slate-400">Target</span>
            <select
              value={formState.targetName}
              onChange={(event) => onChange({ targetName: event.target.value })}
              className="field"
            >
              {catalog.targets.map((target) => (
                <option key={target.name} value={target.name}>
                  {target.name}
                </option>
              ))}
            </select>
          </label>

          <label className="space-y-1">
            <span className="text-xs uppercase tracking-[0.12em] text-slate-400">Campaign Name</span>
            <input
              value={formState.campaignName}
              onChange={(event) => onChange({ campaignName: event.target.value })}
              className="field"
              placeholder="optional-run-label"
            />
          </label>

          <label className="space-y-1">
            <span className="text-xs uppercase tracking-[0.12em] text-slate-400">Category</span>
            <select
              value={formState.category}
              onChange={(event) => onChange({ category: event.target.value as CampaignFormState["category"] })}
              className="field"
            >
              <option value="all">All categories</option>
              {categories.map((category) => (
                <option key={category} value={category}>
                  {formatCategory(category)}
                </option>
              ))}
            </select>
          </label>

          <label className="space-y-1">
            <span className="text-xs uppercase tracking-[0.12em] text-slate-400">Severity</span>
            <select
              value={formState.severity}
              onChange={(event) => onChange({ severity: event.target.value as CampaignFormState["severity"] })}
              className="field"
            >
              <option value="all">All severities</option>
              {severities.map((severity) => (
                <option key={severity} value={severity}>
                  {formatSeverity(severity)}
                </option>
              ))}
            </select>
          </label>

          <label className="space-y-1">
            <span className="text-xs uppercase tracking-[0.12em] text-slate-400">Max Attacks</span>
            <input
              type="number"
              min={1}
              value={formState.maxAttacks}
              onChange={(event) => onChange({ maxAttacks: event.target.value })}
              className="field"
              placeholder="Auto"
            />
          </label>

          <div className="space-y-1">
            <span className="text-xs uppercase tracking-[0.12em] text-slate-400">Persistence</span>
            <label className="flex h-11 items-center gap-2 rounded-lg border border-slate-700/70 bg-slate-900/55 px-3 text-sm text-slate-200">
              <input
                type="checkbox"
                checked={formState.saveAfterExecution}
                onChange={(event) => onChange({ saveAfterExecution: event.target.checked })}
              />
              Save result after execution
            </label>
          </div>
        </div>
      )}

      {defensesEnabled && catalog && (
        <div className="mt-4">
          <p className="text-xs uppercase tracking-[0.12em] text-slate-400">Guarded Defenses</p>
          <div className="mt-2 grid grid-cols-2 gap-2">
            {catalog.defenses.map((defense) => {
              const checked = formState.enabledDefenses.includes(defense.name);
              return (
                <label
                  key={defense.name}
                  className="flex items-center gap-2 rounded-lg border border-slate-700/70 bg-slate-900/55 px-3 py-2 text-sm text-slate-200"
                >
                  <input
                    type="checkbox"
                    checked={checked}
                    onChange={(event) => {
                      if (event.target.checked) {
                        onChange({ enabledDefenses: [...formState.enabledDefenses, defense.name] });
                        return;
                      }
                      onChange({ enabledDefenses: formState.enabledDefenses.filter((item) => item !== defense.name) });
                    }}
                  />
                  <span className="truncate">{defense.name}</span>
                </label>
              );
            })}
          </div>
        </div>
      )}

      <div className="mt-5 flex flex-wrap gap-2">
        <button
          type="button"
          onClick={onRun}
          disabled={running}
          className="rounded-lg bg-cyan-400 px-4 py-2 text-sm font-semibold text-slate-950 transition hover:bg-cyan-300 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {running ? "Executing..." : "Execute"}
        </button>
        <button
          type="button"
          onClick={onRunEvaluateOnly}
          disabled={running}
          className="rounded-lg border border-cyan-300/55 px-4 py-2 text-sm font-semibold text-cyan-100 transition hover:bg-cyan-400/10 disabled:cursor-not-allowed disabled:opacity-50"
        >
          Execute + Evaluate
        </button>

        {running && (
          <div className="ml-2 inline-flex items-center gap-2 rounded-lg bg-slate-900/70 px-3 py-2 text-xs text-slate-200 ring-1 ring-slate-700/70">
            <motion.span
              className="h-2.5 w-2.5 rounded-full bg-cyan-300"
              animate={{ opacity: [0.4, 1, 0.4], scale: [0.9, 1.1, 0.9] }}
              transition={{ repeat: Infinity, duration: 1.1, ease: "easeInOut" }}
            />
            Running {formatDurationMs(runElapsedMs)}
          </div>
        )}
      </div>

      {runError && <p className="mt-3 rounded-lg bg-rose-500/10 p-3 text-sm text-rose-200">{runError}</p>}
    </section>
  );
}
