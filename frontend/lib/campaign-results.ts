import { CampaignAttackResult } from "@/types/api";
import { AttackResultRow, CampaignViewModel } from "@/types/ui";

function truncate(text: string, maxLength: number): string {
  if (text.length <= maxLength) {
    return text;
  }
  return `${text.slice(0, maxLength - 3)}...`;
}

function previewFromRaw(raw: CampaignAttackResult | undefined): string {
  if (!raw || !raw.response_text) {
    return "No response captured.";
  }
  return truncate(raw.response_text.replace(/\s+/g, " ").trim(), 110);
}

function readStringCandidate(value: unknown): string | null {
  return typeof value === "string" && value.trim().length > 0 ? value : null;
}

function getPathValue(source: unknown, path: string[]): unknown {
  let current: unknown = source;
  for (const key of path) {
    if (typeof current !== "object" || current === null || !(key in current)) {
      return undefined;
    }
    current = (current as Record<string, unknown>)[key];
  }
  return current;
}

function extractSystemPrompt(raw: CampaignAttackResult | undefined): string | null {
  if (!raw) {
    return null;
  }

  const metadata: unknown = raw.execution_metadata.raw_target_metadata;
  const directCandidates: unknown[] = [
    getPathValue(metadata, ["system_prompt_used"]),
    getPathValue(metadata, ["sanitized_system_prompt"]),
    getPathValue(metadata, ["system_prompt"]),
    getPathValue(metadata, ["final_system_prompt"]),
    getPathValue(metadata, ["defense_summary", "final_system_prompt"]),
    getPathValue(metadata, ["defense_summary", "final_summary", "final_system_prompt"]),
    getPathValue(metadata, ["request_metadata", "system_prompt_override"]),
  ];

  for (const candidate of directCandidates) {
    const asString = readStringCandidate(candidate);
    if (asString) {
      return asString;
    }
  }

  return null;
}

export function buildAttackRows(view: CampaignViewModel): AttackResultRow[] {
  const rawById = new Map<string, CampaignAttackResult>();
  if (view.run) {
    for (const raw of view.run.results) {
      rawById.set(raw.attack_id, raw);
    }
  }

  return view.evaluated.evaluations.map((evaluation) => {
    const raw = rawById.get(evaluation.attack_id);
    return {
      attackId: evaluation.attack_id,
      attackName: evaluation.attack_name,
      category: evaluation.category,
      severity: evaluation.severity,
      targetName: evaluation.target_name,
      classification: evaluation.classification,
      executionStatus: raw?.execution_status ?? "unknown",
      warningsCount: raw?.warnings.length ?? 0,
      flagsCount: raw?.flags.length ?? 0,
      responsePreview: previewFromRaw(raw),
      attackPromptFull: raw?.attack_prompt_snapshot ?? null,
      responseFull: raw?.response_text ?? null,
      systemPromptFull: extractSystemPrompt(raw),
      reasoningSummary: evaluation.reasoning_summary,
      matchedSignals: evaluation.matched_signals,
      matchedRules: evaluation.matched_rules,
      responseExcerpt: evaluation.response_excerpt,
      rawResult: raw,
      evaluation
    };
  });
}
