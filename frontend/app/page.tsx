"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { motion } from "framer-motion";

import { CenterWorkspace } from "@/components/center-workspace";
import { InspectorPanel } from "@/components/inspector-panel";
import { LabHeader } from "@/components/lab-header";
import { SavedCampaignsSidebar } from "@/components/saved-campaigns-sidebar";
import { buildAttackRows } from "@/lib/campaign-results";
import {
  executeEvaluate,
  executeEvaluateSave,
  getReadiness,
  getSavedCampaign,
  getWorkflowCatalog,
  listSavedCampaigns
} from "@/lib/api-client";
import {
  CampaignRunRequest,
  ReadinessResponse,
  SavedCampaignSummary,
  WorkflowCatalogResponse
} from "@/types/api";
import { CampaignFormState, CampaignViewModel, CenterWorkspaceMode, toCampaignView } from "@/types/ui";

function buildRequestPayload(formState: CampaignFormState): CampaignRunRequest {
  const maxAttacksParsed = formState.maxAttacks.trim() ? Number(formState.maxAttacks.trim()) : undefined;

  return {
    campaign_name: formState.campaignName.trim() || undefined,
    target_name: formState.targetName,
    category: formState.category === "all" ? undefined : formState.category,
    severity: formState.severity === "all" ? undefined : formState.severity,
    max_attacks: maxAttacksParsed && maxAttacksParsed > 0 ? maxAttacksParsed : undefined,
    enabled_defenses: formState.targetName === "guarded_chat" ? formState.enabledDefenses : undefined,
    metadata: {
      source: "frontend_mvp"
    }
  };
}

export default function HomePage() {
  const [catalog, setCatalog] = useState<WorkflowCatalogResponse | null>(null);
  const [catalogLoading, setCatalogLoading] = useState(true);
  const [catalogError, setCatalogError] = useState<string | null>(null);

  const [savedCampaigns, setSavedCampaigns] = useState<SavedCampaignSummary[]>([]);
  const [savedLoading, setSavedLoading] = useState(true);
  const [savedError, setSavedError] = useState<string | null>(null);

  const [readiness, setReadiness] = useState<ReadinessResponse | null>(null);
  const [readinessLoading, setReadinessLoading] = useState(true);

  const [activeView, setActiveView] = useState<CampaignViewModel | null>(null);
  const [selectedSavedRunId, setSelectedSavedRunId] = useState<string | null>(null);
  const [selectedAttackId, setSelectedAttackId] = useState<string | null>(null);

  const [running, setRunning] = useState(false);
  const [runElapsedMs, setRunElapsedMs] = useState(0);
  const [runStartedAtMs, setRunStartedAtMs] = useState<number | null>(null);
  const [runError, setRunError] = useState<string | null>(null);

  const [formState, setFormState] = useState<CampaignFormState>({
    campaignName: "",
    targetName: "simple_vulnerable_chat",
    category: "all",
    severity: "all",
    maxAttacks: "",
    saveAfterExecution: true,
    enabledDefenses: []
  });
  const centerMode: CenterWorkspaceMode = activeView ? "results" : "setup";

  const refreshSavedCampaigns = useCallback(async () => {
    setSavedLoading(true);
    setSavedError(null);
    try {
      const campaigns = await listSavedCampaigns();
      setSavedCampaigns(campaigns);
    } catch (error) {
      setSavedError(error instanceof Error ? error.message : "Failed to fetch saved campaigns.");
    } finally {
      setSavedLoading(false);
    }
  }, []);

  const refreshReadiness = useCallback(async () => {
    setReadinessLoading(true);
    try {
      const readinessResponse = await getReadiness();
      setReadiness(readinessResponse);
    } catch {
      setReadiness(null);
    } finally {
      setReadinessLoading(false);
    }
  }, []);

  useEffect(() => {
    let cancelled = false;

    async function bootstrap() {
      setCatalogLoading(true);
      setCatalogError(null);
      try {
        const catalogResponse = await getWorkflowCatalog();
        if (cancelled) {
          return;
        }
        setCatalog(catalogResponse);
        setFormState((current) => ({
          ...current,
          targetName: current.targetName || catalogResponse.default_target,
          enabledDefenses: catalogResponse.guarded_default_defenses
        }));
      } catch (error) {
        if (!cancelled) {
          setCatalogError(error instanceof Error ? error.message : "Failed to fetch workflow catalog.");
        }
      } finally {
        if (!cancelled) {
          setCatalogLoading(false);
        }
      }
    }

    bootstrap();
    refreshSavedCampaigns();
    refreshReadiness();

    return () => {
      cancelled = true;
    };
  }, [refreshSavedCampaigns, refreshReadiness]);

  const attackRows = useMemo(() => {
    if (!activeView) {
      return [];
    }
    return buildAttackRows(activeView);
  }, [activeView]);

  const selectedAttackRow = useMemo(() => {
    if (attackRows.length === 0) {
      return null;
    }
    if (!selectedAttackId) {
      return attackRows[0];
    }
    return attackRows.find((row) => row.attackId === selectedAttackId) ?? attackRows[0];
  }, [attackRows, selectedAttackId]);

  useEffect(() => {
    if (attackRows.length > 0) {
      setSelectedAttackId(attackRows[0].attackId);
    } else {
      setSelectedAttackId(null);
    }
  }, [activeView, attackRows]);

  useEffect(() => {
    if (!running || runStartedAtMs === null) {
      return;
    }

    const timerId = window.setInterval(() => {
      setRunElapsedMs(Date.now() - runStartedAtMs);
    }, 250);

    return () => {
      window.clearInterval(timerId);
    };
  }, [running, runStartedAtMs]);

  const runWorkflow = useCallback(
    async (forceSave: boolean) => {
      setRunError(null);
      if (readiness && readiness.status !== "ok") {
        const degraded = readiness.components
          .filter((component) => component.status !== "ok")
          .map((component) => `${component.name}: ${component.detail ?? component.status}`)
          .join(" | ");
        setRunError(`Runtime not ready. ${degraded || "Check Ollama and SQLite status."}`);
        return;
      }
      const startedAt = Date.now();
      setRunStartedAtMs(startedAt);
      setRunElapsedMs(0);
      setRunning(true);
      try {
        const payload = buildRequestPayload(formState);
        if (forceSave) {
          const saved = await executeEvaluateSave(payload);
          const view = toCampaignView(saved);
          setActiveView(view);
          setSelectedSavedRunId(saved.run_result.run_id);
          await refreshSavedCampaigns();
        } else {
          const evaluated = await executeEvaluate(payload);
          setActiveView({
            source: "transient",
            run: null,
            evaluated
          });
          setSelectedSavedRunId(null);
        }
        await refreshReadiness();
      } catch (error) {
        setRunError(error instanceof Error ? error.message : "Failed to execute workflow.");
      } finally {
        setRunElapsedMs(Date.now() - startedAt);
        setRunning(false);
        setRunStartedAtMs(null);
      }
    },
    [formState, readiness, refreshReadiness, refreshSavedCampaigns]
  );

  const handleSelectSavedCampaign = useCallback(async (runId: string) => {
    setRunError(null);
    setSelectedSavedRunId(runId);
    try {
      const record = await getSavedCampaign(runId);
      setActiveView(toCampaignView(record));
    } catch (error) {
      setRunError(error instanceof Error ? error.message : "Failed to load saved campaign.");
    }
  }, []);

  const handleFormPatch = useCallback((patch: Partial<CampaignFormState>) => {
    setFormState((current) => ({ ...current, ...patch }));
  }, []);

  const applyVulnerablePreset = useCallback(() => {
    setFormState((current) => ({
      ...current,
      targetName: "simple_vulnerable_chat",
      enabledDefenses: []
    }));
  }, []);

  const applyGuardedPreset = useCallback(() => {
    if (!catalog) {
      return;
    }
    setFormState((current) => ({
      ...current,
      targetName: "guarded_chat",
      enabledDefenses: catalog.guarded_default_defenses
    }));
  }, [catalog]);

  return (
    <main className="relative h-screen overflow-hidden bg-[#070d1a] text-slate-100">
      <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_20%_5%,rgba(34,211,238,0.16),transparent_35%),radial-gradient(circle_at_85%_20%,rgba(16,185,129,0.10),transparent_40%),linear-gradient(180deg,rgba(15,23,42,0.45),rgba(2,6,23,0.92))]" />
      <div className="relative mx-auto flex h-full max-w-[1720px] flex-col p-4">
        <div className="shrink-0">
          <LabHeader compact />
        </div>

        <div className="mt-3 grid min-h-0 flex-1 grid-cols-12 gap-3">
          <motion.div
            initial={{ opacity: 0, x: -8 }}
            animate={{ opacity: 1, x: 0 }}
            className="col-span-3 h-full min-h-0"
          >
            <SavedCampaignsSidebar
              campaigns={savedCampaigns}
              selectedRunId={selectedSavedRunId}
              loading={savedLoading}
              error={savedError}
              readiness={readiness}
              readinessLoading={readinessLoading}
              onSelectCampaign={handleSelectSavedCampaign}
              onNewRun={() => {
                setSelectedSavedRunId(null);
                setActiveView(null);
                setRunError(null);
              }}
            />
          </motion.div>

          <CenterWorkspace
            mode={centerMode}
            catalog={catalog}
            catalogLoading={catalogLoading}
            runError={runError ?? catalogError}
            formState={formState}
            running={running}
            runElapsedMs={runElapsedMs}
            activeView={activeView}
            attackRows={attackRows}
            selectedAttackId={selectedAttackId}
            onSelectAttack={(attackId) => setSelectedAttackId(attackId)}
            onFormChange={handleFormPatch}
            onApplyVulnerablePreset={applyVulnerablePreset}
            onApplyGuardedDefaultPreset={applyGuardedPreset}
            onRun={() => runWorkflow(formState.saveAfterExecution)}
            onRunEvaluateOnly={() => runWorkflow(false)}
          />

          <motion.div
            initial={{ opacity: 0, x: 8 }}
            animate={{ opacity: 1, x: 0 }}
            className="col-span-3 h-full min-h-0"
          >
            <InspectorPanel view={activeView} selectedRow={selectedAttackRow} />
          </motion.div>
        </div>
      </div>
    </main>
  );
}
