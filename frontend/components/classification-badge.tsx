import { EvaluationClassification } from "@/types/api";
import { classificationClassName, formatClassification } from "@/lib/presenters";

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
      <span className="mr-1.5 inline-block h-1.5 w-1.5 rounded-full bg-current opacity-90" />
      {formatClassification(classification)}
    </span>
  );
}
