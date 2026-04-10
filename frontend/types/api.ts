export type AttackCategory =
  | "jailbreak_basic"
  | "prompt_injection_direct"
  | "system_prompt_extraction"
  | "policy_bypass"
  | "data_leakage_simulation";

export type AttackSeverity = "low" | "medium" | "high";

export type EvaluationClassification = "success" | "failed" | "ambiguous";

export interface TargetDescriptor {
  name: string;
  mode: string;
  defense_mode: string;
  description: string;
}

export interface DefenseDescriptor {
  name: string;
  stage: string;
  description: string;
}

export interface AttackCategoryCount {
  category: AttackCategory;
  count: number;
}

export interface WorkflowCatalogResponse {
  default_target: string;
  targets: TargetDescriptor[];
  defenses: DefenseDescriptor[];
  guarded_default_defenses: string[];
  total_attacks: number;
  attack_categories: AttackCategoryCount[];
}

export interface ComponentReadiness {
  name: "llm" | "sqlite" | string;
  status: "ok" | "unavailable" | string;
  detail?: string | null;
}

export interface ReadinessResponse {
  app_name: string;
  environment: string;
  status: "ok" | "degraded" | string;
  components: ComponentReadiness[];
}

export interface CampaignRunRequest {
  campaign_name?: string | null;
  target_name: string;
  attack_ids?: string[];
  category?: AttackCategory | null;
  severity?: AttackSeverity | null;
  model_override?: string | null;
  system_prompt_override?: string | null;
  enabled_defenses?: string[] | null;
  max_attacks?: number | null;
  stop_on_error?: boolean;
  metadata?: Record<string, unknown>;
}

export interface CampaignAggregateCounts {
  selected_attacks: number;
  executed_attacks: number;
  succeeded_attacks: number;
  failed_attacks: number;
}

export interface AttackExecutionMetadataSnapshot {
  final_prompt_summary?: string | null;
  risk_level?: string | null;
  llm_called?: boolean | null;
  prompt_source?: string | null;
  target_mode?: string | null;
  raw_target_metadata?: Record<string, unknown>;
}

export interface CampaignAttackResult {
  attack_id: string;
  attack_name: string;
  category: AttackCategory;
  severity: AttackSeverity;
  target_name: string;
  target_name_snapshot?: string | null;
  defense_mode?: string | null;
  attack_prompt_snapshot?: string | null;
  attack_description_snapshot?: string | null;
  model: string;
  response_text: string;
  warnings: string[];
  flags: string[];
  execution_metadata: AttackExecutionMetadataSnapshot;
  execution_status: "succeeded" | "failed";
  error_message?: string | null;
  started_at: string;
  completed_at: string;
}

export interface CampaignRunResult {
  run_id: string;
  campaign_name: string;
  state: "starting" | "running" | "completed" | "completed_with_errors" | "failed";
  target_name: string;
  category_filter?: AttackCategory | null;
  severity_filter?: AttackSeverity | null;
  attack_ids_filter?: string[];
  stop_on_error: boolean;
  model_override?: string | null;
  enabled_defenses?: string[] | null;
  system_prompt_override_used: boolean;
  metadata: Record<string, unknown>;
  started_at: string;
  completed_at: string;
  counts: CampaignAggregateCounts;
  results: CampaignAttackResult[];
}

export interface MatchedRule {
  rule_id: string;
  signal: string;
  evidence: string;
}

export interface AttackEvaluationResult {
  attack_id: string;
  attack_name: string;
  category: AttackCategory;
  severity: AttackSeverity;
  target_name: string;
  classification: EvaluationClassification;
  matched_signals: string[];
  matched_rules: MatchedRule[];
  reasoning_summary: string;
  response_excerpt?: string | null;
  source_execution_status: "succeeded" | "failed";
}

export interface CategoryEvaluationBreakdown {
  category: AttackCategory;
  total: number;
  success: number;
  failed: number;
  ambiguous: number;
  success_rate: number;
}

export interface SeverityEvaluationBreakdown {
  severity: AttackSeverity;
  total: number;
  success: number;
  failed: number;
  ambiguous: number;
  success_rate: number;
}

export interface CampaignEvaluationSummary {
  total_attacks: number;
  success_count: number;
  failed_count: number;
  ambiguous_count: number;
  success_rate_overall: number;
  failed_rate_overall: number;
  ambiguous_rate_overall: number;
  per_category: CategoryEvaluationBreakdown[];
  per_severity: SeverityEvaluationBreakdown[];
}

export interface EvaluatedCampaignResult {
  run_id: string;
  campaign_name: string;
  target_name: string;
  evaluated_at: string;
  source_started_at: string;
  source_completed_at: string;
  evaluations: AttackEvaluationResult[];
  summary: CampaignEvaluationSummary;
}

export interface SaveEvaluatedCampaignRequest {
  run_result: CampaignRunResult;
  evaluated_result: EvaluatedCampaignResult;
}

export interface SavedCampaignSummary {
  run_id: string;
  campaign_name: string;
  target_name: string;
  pipeline_state: string;
  completed_at: string;
  evaluated_at: string;
  total_attacks: number;
  success_count: number;
  failed_count: number;
  ambiguous_count: number;
  success_rate_overall: number;
}

export interface SavedCampaignRecord {
  saved_at: string;
  run_result: CampaignRunResult;
  evaluated_result: EvaluatedCampaignResult;
}
