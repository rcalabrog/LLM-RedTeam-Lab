import { CampaignAttackResult } from "@/types/api";
import { AttackResultRow, CampaignViewModel } from "@/types/ui";

function truncate(text: string, maxLength: number): string {
  if (text.length <= maxLength) {
    return text;
  }
  return `${text.slice(0, maxLength - 1)}…`;
}

function previewFromRaw(raw: CampaignAttackResult | undefined): string {
  if (!raw || !raw.response_text) {
    return "No response captured.";
  }
  return truncate(raw.response_text.replace(/\s+/g, " ").trim(), 110);
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
      reasoningSummary: evaluation.reasoning_summary,
      matchedSignals: evaluation.matched_signals,
      matchedRules: evaluation.matched_rules,
      responseExcerpt: evaluation.response_excerpt,
      rawResult: raw,
      evaluation
    };
  });
}
