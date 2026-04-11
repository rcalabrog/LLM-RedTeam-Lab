import { useEffect, useMemo, useState } from "react";
import { motion } from "framer-motion";

import { CampaignConfigurator } from "@/components/campaign-configurator";
import { CampaignResultsPanel } from "@/components/campaign-results-panel";
import { CampaignSummary } from "@/components/campaign-summary";
import { CollapsibleSection } from "@/components/collapsible-section";
import { formatCategory } from "@/lib/presenters";
import { WorkflowCatalogResponse } from "@/types/api";
import { AttackResultRow, CampaignFormState, CampaignViewModel, CenterWorkspaceMode } from "@/types/ui";

type CenterSectionKey = "setup" | "catalog" | "current" | "results";

interface CenterWorkspaceProps {
  mode: CenterWorkspaceMode;
  catalog: WorkflowCatalogResponse | null;
  catalogLoading: boolean;
  runError: string | null;
  formState: CampaignFormState;
  running: boolean;
  runElapsedMs: number;
  activeView: CampaignViewModel | null;
  attackRows: AttackResultRow[];
  selectedAttackId: string | null;
  onSelectAttack: (attackId: string) => void;
  onFormChange: (patch: Partial<CampaignFormState>) => void;
  onApplyVulnerablePreset: () => void;
  onApplyGuardedDefaultPreset: () => void;
  onRun: () => void;
  onRunEvaluateOnly: () => void;
}

function defaultSectionState(mode: CenterWorkspaceMode, hasActiveResult: boolean): Record<CenterSectionKey, boolean> {
  if (mode === "results" && hasActiveResult) {
    return {
      setup: false,
      catalog: false,
      current: true,
      results: true
    };
  }

  return {
    setup: true,
    catalog: true,
    current: false,
    results: false
  };
}

export function CenterWorkspace({
  mode,
  catalog,
  catalogLoading,
  runError,
  formState,
  running,
  runElapsedMs,
  activeView,
  attackRows,
  selectedAttackId,
  onSelectAttack,
  onFormChange,
  onApplyVulnerablePreset,
  onApplyGuardedDefaultPreset,
  onRun,
  onRunEvaluateOnly
}: CenterWorkspaceProps) {
  const hasActiveResult = Boolean(activeView);
  const [openSections, setOpenSections] = useState<Record<CenterSectionKey, boolean>>(
    defaultSectionState(mode, hasActiveResult)
  );

  useEffect(() => {
    setOpenSections(defaultSectionState(mode, hasActiveResult));
  }, [mode, hasActiveResult]);

  const catalogSubtitle = useMemo(() => {
    if (catalogLoading) {
      return "Loading categories...";
    }
    if (!catalog) {
      return "Catalog unavailable";
    }
    return `${catalog.attack_categories.length} categories`;
  }, [catalog, catalogLoading]);

  const currentSubtitle = useMemo(() => {
    if (!activeView) {
      return "No campaign loaded";
    }
    return `${activeView.evaluated.campaign_name}`;
  }, [activeView]);

  const resultsSubtitle = selectedAttackId
    ? `${attackRows.length} rows | selected: ${selectedAttackId}`
    : `${attackRows.length} rows`;

  return (
    <motion.section
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      className="col-span-6 h-full min-h-0 overflow-hidden"
    >
      <div className="flex h-full min-h-0 flex-col gap-2">
        <div className="shrink-0 space-y-2">
          <CollapsibleSection
            title="Global Campaign Setup"
            subtitle={mode === "results" ? "Compact rerun controls" : "Configure a new campaign"}
            open={openSections.setup}
            onToggle={() => setOpenSections((current) => ({ ...current, setup: !current.setup }))}
            contentClassName="p-0"
          >
            <CampaignConfigurator
              catalog={catalog}
              loading={catalogLoading}
              mode={mode}
              formState={formState}
              running={running}
              runElapsedMs={runElapsedMs}
              runError={runError}
              onChange={onFormChange}
              onApplyVulnerablePreset={onApplyVulnerablePreset}
              onApplyGuardedDefaultPreset={onApplyGuardedDefaultPreset}
              onRun={onRun}
              onRunEvaluateOnly={onRunEvaluateOnly}
              embedded
            />
          </CollapsibleSection>

          <CollapsibleSection
            title="Attack Catalog Snapshot"
            subtitle={catalogSubtitle}
            open={openSections.catalog}
            onToggle={() => setOpenSections((current) => ({ ...current, catalog: !current.catalog }))}
            contentClassName="p-2"
          >
            {!catalog ? (
              <p className="text-xs text-slate-300">
                {catalogLoading ? "Loading attack categories..." : "Catalog is unavailable."}
              </p>
            ) : (
              <div className="flex flex-wrap gap-1.5">
                {catalog.attack_categories.map((item) => (
                  <span key={item.category} className="rounded-full bg-slate-800/70 px-2 py-0.5 text-[11px] text-slate-200">
                    {formatCategory(item.category)}: {item.count}
                  </span>
                ))}
              </div>
            )}
          </CollapsibleSection>

          <CollapsibleSection
            title="Current Campaign"
            subtitle={currentSubtitle}
            open={openSections.current}
            onToggle={() => setOpenSections((current) => ({ ...current, current: !current.current }))}
            contentClassName="p-2"
          >
            <CampaignSummary view={activeView} mode={mode} embedded />
          </CollapsibleSection>
        </div>

        <div className="min-h-0 flex-1">
          <CollapsibleSection
            title="Campaign Results"
            subtitle={resultsSubtitle}
            open={openSections.results}
            onToggle={() => setOpenSections((current) => ({ ...current, results: !current.results }))}
            fill
            className="h-full"
            contentClassName="min-h-0 flex flex-1 flex-col p-2"
          >
            <CampaignResultsPanel
              mode={mode}
              rows={attackRows}
              selectedAttackId={selectedAttackId}
              onSelectRow={onSelectAttack}
              embedded
            />
          </CollapsibleSection>
        </div>
      </div>
    </motion.section>
  );
}
