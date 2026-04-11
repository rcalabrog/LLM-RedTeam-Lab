import {
  AttackCategory,
  AttackEvaluationResult,
  AttackSeverity,
  CampaignAttackResult,
  CampaignRunResult,
  EvaluatedCampaignResult,
  SavedCampaignRecord
} from "@/types/api";

export interface CampaignFormState {
  campaignName: string;
  targetName: string;
  category: AttackCategory | "all";
  severity: AttackSeverity | "all";
  maxAttacks: string;
  saveAfterExecution: boolean;
  enabledDefenses: string[];
}

export type CenterWorkspaceMode = "setup" | "results";

export interface CampaignViewModel {
  source: "transient" | "saved";
  run: CampaignRunResult | null;
  evaluated: EvaluatedCampaignResult;
  savedAt?: string;
}

export interface AttackResultRow {
  attackId: string;
  attackName: string;
  category: AttackCategory;
  severity: AttackSeverity;
  targetName: string;
  classification: AttackEvaluationResult["classification"];
  executionStatus: CampaignAttackResult["execution_status"] | "unknown";
  warningsCount: number;
  flagsCount: number;
  responsePreview: string;
  attackPromptFull?: string | null;
  responseFull?: string | null;
  systemPromptFull?: string | null;
  reasoningSummary: string;
  matchedSignals: string[];
  matchedRules: AttackEvaluationResult["matched_rules"];
  responseExcerpt?: string | null;
  rawResult?: CampaignAttackResult;
  evaluation: AttackEvaluationResult;
}

export type Loadable<T> =
  | { status: "idle" | "loading"; data: null; error: null }
  | { status: "ready"; data: T; error: null }
  | { status: "error"; data: null; error: string };

export function toCampaignView(record: SavedCampaignRecord): CampaignViewModel {
  return {
    source: "saved",
    run: record.run_result,
    evaluated: record.evaluated_result,
    savedAt: record.saved_at
  };
}
