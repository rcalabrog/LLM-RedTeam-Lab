import type React from "react";

import { AttackCatalogPanel } from "@/components/attack-catalog-panel";
import { CampaignConfigurator } from "@/components/campaign-configurator";
import { AttackDefinition, WorkflowCatalogResponse } from "@/types/api";
import { CampaignFormState } from "@/types/ui";

interface SetupViewProps {
  savedCampaignsSlot: React.ReactNode;
  catalog: WorkflowCatalogResponse | null;
  catalogLoading: boolean;
  attackDefinitions: AttackDefinition[];
  attackDefinitionsLoading: boolean;
  attackDefinitionsError: string | null;
  runError: string | null;
  formState: CampaignFormState;
  running: boolean;
  runElapsedMs: number;
  onFormChange: (patch: Partial<CampaignFormState>) => void;
  onApplyVulnerablePreset: () => void;
  onApplyGuardedDefaultPreset: () => void;
  onRun: () => void;
  onRunEvaluateOnly: () => void;
}

export function SetupView({
  savedCampaignsSlot,
  catalog,
  catalogLoading,
  attackDefinitions,
  attackDefinitionsLoading,
  attackDefinitionsError,
  runError,
  formState,
  running,
  runElapsedMs,
  onFormChange,
  onApplyVulnerablePreset,
  onApplyGuardedDefaultPreset,
  onRun,
  onRunEvaluateOnly
}: SetupViewProps) {
  return (
    <div className="mt-3 grid min-h-0 flex-1 grid-cols-[3fr_6fr_3fr] gap-3">
      <div className="h-full min-h-0">{savedCampaignsSlot}</div>

      <section className="h-full min-h-0 overflow-y-auto rounded-2xl border border-slate-700/70 bg-slate-900/60 p-4 backdrop-blur">
        <header className="border-b border-slate-700/60 pb-3">
          <h2 className="text-lg font-semibold text-slate-100">Campaign Setup</h2>
          <p className="mt-1 text-sm text-slate-300">
            Configure the target, filters, persistence, and execution mode for the next campaign.
          </p>
        </header>
        <div className="mt-4">
          <CampaignConfigurator
            catalog={catalog}
            loading={catalogLoading}
            mode="setup"
            embedded
            formState={formState}
            running={running}
            runElapsedMs={runElapsedMs}
            runError={runError}
            onChange={onFormChange}
            onApplyVulnerablePreset={onApplyVulnerablePreset}
            onApplyGuardedDefaultPreset={onApplyGuardedDefaultPreset}
            onRun={onRun}
            onRunEvaluateOnly={onRunEvaluateOnly}
          />
        </div>
      </section>

      <div className="h-full min-h-0">
        <AttackCatalogPanel
          attacks={attackDefinitions}
          loading={attackDefinitionsLoading}
          error={attackDefinitionsError}
        />
      </div>
    </div>
  );
}
