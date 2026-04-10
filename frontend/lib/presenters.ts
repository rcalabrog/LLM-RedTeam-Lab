import { AttackCategory, AttackSeverity, EvaluationClassification } from "@/types/api";

const categoryLabelMap: Record<AttackCategory, string> = {
  jailbreak_basic: "Jailbreak",
  prompt_injection_direct: "Prompt Injection",
  system_prompt_extraction: "Prompt Extraction",
  policy_bypass: "Policy Bypass",
  data_leakage_simulation: "Data Leakage"
};

const severityLabelMap: Record<AttackSeverity, string> = {
  low: "Low",
  medium: "Medium",
  high: "High"
};

export function formatCategory(category: AttackCategory): string {
  return categoryLabelMap[category];
}

export function formatSeverity(severity: AttackSeverity): string {
  return severityLabelMap[severity];
}

export function formatDateTime(value: string): string {
  return new Date(value).toLocaleString(undefined, {
    dateStyle: "medium",
    timeStyle: "short"
  });
}

export function formatRate(value: number): string {
  return `${(value * 100).toFixed(1)}%`;
}

export function classificationClassName(classification: EvaluationClassification): string {
  switch (classification) {
    case "success":
      return "bg-rose-500/20 text-rose-200 ring-1 ring-rose-400/40";
    case "failed":
      return "bg-emerald-500/20 text-emerald-200 ring-1 ring-emerald-400/40";
    case "ambiguous":
    default:
      return "bg-amber-500/20 text-amber-200 ring-1 ring-amber-400/40";
  }
}
