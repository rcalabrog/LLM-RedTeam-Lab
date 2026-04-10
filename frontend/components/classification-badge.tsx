import { EvaluationClassification } from "@/types/api";
import { classificationClassName } from "@/lib/presenters";

interface ClassificationBadgeProps {
  classification: EvaluationClassification;
}

export function ClassificationBadge({ classification }: ClassificationBadgeProps) {
  return (
    <span
      className={`inline-flex min-w-24 items-center justify-center rounded-full px-2.5 py-1 text-xs font-semibold uppercase tracking-[0.12em] ${classificationClassName(
        classification
      )}`}
    >
      {classification}
    </span>
  );
}
