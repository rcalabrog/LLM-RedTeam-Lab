import { AttackCategory, AttackSeverity, WorkflowCatalogResponse } from "@/types/api";
import { CampaignFormState, CenterWorkspaceMode } from "@/types/ui";
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
  mode: CenterWorkspaceMode;
  embedded?: boolean;
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
  mode,
  embedded = false,
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
  const isResultsMode = mode === "results";
  const defensesEnabled = formState.targetName === "guarded_chat";
  const compactField = isResultsMode ? "field h-10 text-xs" : "field";
  const compactLabel = isResultsMode ? "text-[11px] uppercase tracking-[0.11em] text-slate-400" : "text-xs uppercase tracking-[0.12em] text-slate-400";
  const content = (
    <>
      {!embedded && (
        <div className={`border-b border-slate-700/60 ${isResultsMode ? "pb-2" : "pb-3"}`}>
          <h2 className={`font-semibold text-slate-100 ${isResultsMode ? "text-base" : "text-lg"}`}>
            Campaign Configuration
          </h2>
          <p className={`mt-1 text-slate-300 ${isResultsMode ? "text-xs" : "text-sm"}`}>
            {isResultsMode
              ? "Adjust filters or target presets without leaving result inspection."
              : "Configure one attack batch and run deterministic evaluation for vulnerable vs defended targets."}
          </p>
        </div>
      )}

      <div className={`flex flex-wrap items-center gap-2 ${embedded ? "mb-2" : isResultsMode ? "mt-2 mb-2" : "mt-3 mb-3"}`}>
        <button
          type="button"
          onClick={onApplyVulnerablePreset}
          className={`rounded-lg border border-slate-600 font-semibold text-slate-200 transition hover:border-slate-400 ${
            isResultsMode ? "px-2.5 py-1 text-[11px]" : "px-3 py-1.5 text-xs"
          }`}
        >
          Vulnerable Baseline
        </button>
        <button
          type="button"
          onClick={onApplyGuardedDefaultPreset}
          className={`rounded-lg border border-cyan-400/50 font-semibold text-cyan-200 transition hover:bg-cyan-500/10 ${
            isResultsMode ? "px-2.5 py-1 text-[11px]" : "px-3 py-1.5 text-xs"
          }`}
        >
          Guarded Default
        </button>
      </div>

      {loading && (
        <p className={`rounded-lg bg-slate-900/60 text-slate-300 ${isResultsMode ? "p-2 text-xs" : "p-3 text-sm"}`}>
          Loading catalog configuration...
        </p>
      )}

      {!loading && catalog && (
        <div className={`grid ${isResultsMode ? "grid-cols-3 gap-2" : "grid-cols-2 gap-3"}`}>
          <label className="space-y-1">
            <span className={compactLabel}>Target</span>
            <select
              value={formState.targetName}
              onChange={(event) => onChange({ targetName: event.target.value })}
              className={compactField}
            >
              {catalog.targets.map((target) => (
                <option key={target.name} value={target.name}>
                  {target.name}
                </option>
              ))}
            </select>
          </label>

          <label className="space-y-1">
            <span className={compactLabel}>Campaign Name</span>
            <input
              value={formState.campaignName}
              onChange={(event) => onChange({ campaignName: event.target.value })}
              className={compactField}
              placeholder="optional-run-label"
            />
          </label>

          <label className="space-y-1">
            <span className={compactLabel}>Category</span>
            <select
              value={formState.category}
              onChange={(event) => onChange({ category: event.target.value as CampaignFormState["category"] })}
              className={compactField}
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
            <span className={compactLabel}>Severity</span>
            <select
              value={formState.severity}
              onChange={(event) => onChange({ severity: event.target.value as CampaignFormState["severity"] })}
              className={compactField}
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
            <span className={compactLabel}>Max Attacks</span>
            <input
              type="number"
              min={1}
              value={formState.maxAttacks}
              onChange={(event) => onChange({ maxAttacks: event.target.value })}
              className={compactField}
              placeholder="Auto"
            />
          </label>

          <div className="space-y-1">
            <span className={compactLabel}>Persistence</span>
            <label
              className={`flex items-center gap-2 rounded-lg border border-slate-700/70 bg-slate-900/55 px-3 text-slate-200 ${
                isResultsMode ? "h-10 text-xs" : "h-11 text-sm"
              }`}
            >
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
        <div className={`rounded-xl border border-slate-700/60 bg-slate-900/45 ${isResultsMode ? "mt-2 p-2.5" : "mt-4 p-3"}`}>
          <p className={compactLabel}>Guarded Defenses</p>
          <div className={`grid gap-2 ${isResultsMode ? "mt-1.5 grid-cols-3" : "mt-2 grid-cols-2"}`}>
            {catalog.defenses.map((defense) => {
              const checked = formState.enabledDefenses.includes(defense.name);
              return (
                <label
                  key={defense.name}
                  className={`flex items-center gap-2 rounded-lg border border-slate-700/70 bg-slate-900/55 text-slate-200 ${
                    isResultsMode ? "px-2 py-1.5 text-xs" : "px-3 py-2 text-sm"
                  }`}
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

      <div className={`flex flex-wrap gap-2 ${isResultsMode ? "mt-2" : "mt-5"}`}>
        <button
          type="button"
          onClick={onRun}
          disabled={running}
          className={`rounded-lg bg-cyan-400 font-semibold text-slate-950 transition hover:bg-cyan-300 disabled:cursor-not-allowed disabled:opacity-50 ${
            isResultsMode ? "px-3 py-1.5 text-xs" : "px-4 py-2 text-sm"
          }`}
        >
          {running ? "Executing..." : "Execute"}
        </button>
        <button
          type="button"
          onClick={onRunEvaluateOnly}
          disabled={running}
          className={`rounded-lg border border-cyan-300/55 font-semibold text-cyan-100 transition hover:bg-cyan-400/10 disabled:cursor-not-allowed disabled:opacity-50 ${
            isResultsMode ? "px-3 py-1.5 text-xs" : "px-4 py-2 text-sm"
          }`}
        >
          Execute + Evaluate
        </button>

        {running && (
          <div
            className={`inline-flex items-center gap-2 rounded-lg bg-slate-900/70 text-slate-200 ring-1 ring-slate-700/70 ${
              isResultsMode ? "px-2 py-1 text-[11px]" : "ml-2 px-3 py-2 text-xs"
            }`}
          >
            <motion.span
              className="h-2.5 w-2.5 rounded-full bg-cyan-300"
              animate={{ opacity: [0.4, 1, 0.4], scale: [0.9, 1.1, 0.9] }}
              transition={{ repeat: Infinity, duration: 1.1, ease: "easeInOut" }}
            />
            Running {formatDurationMs(runElapsedMs)}
          </div>
        )}
      </div>

      {runError && (
        <p className={`rounded-lg bg-rose-500/10 text-rose-200 ${isResultsMode ? "mt-2 p-2 text-xs" : "mt-3 p-3 text-sm"}`}>
          {runError}
        </p>
      )}
    </>
  );

  return (
    embedded ? (
      <div className={isResultsMode ? "p-2" : "p-3"}>{content}</div>
    ) : (
      <motion.section
        layout
        transition={{ duration: 0.2, ease: "easeOut" }}
        className="shrink-0 rounded-2xl border border-slate-700/70 bg-slate-900/60 p-4 backdrop-blur"
      >
        {content}
      </motion.section>
    )
  );
}
