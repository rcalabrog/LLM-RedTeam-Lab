import { ClassificationBadge } from "@/components/classification-badge";
import { formatCategory, formatSeverity } from "@/lib/presenters";
import { AttackResultRow } from "@/types/ui";

interface AttackResultsTableProps {
  rows: AttackResultRow[];
  selectedAttackId: string | null;
  onSelectRow: (attackId: string) => void;
}

export function AttackResultsTable({ rows, selectedAttackId, onSelectRow }: AttackResultsTableProps) {
  if (rows.length === 0) {
    return (
      <div className="flex h-full min-h-0 items-center rounded-xl border border-slate-700/70 bg-slate-900/60 p-6 text-sm text-slate-300">
        No attack rows available yet.
      </div>
    );
  }

  return (
    <div className="relative isolate h-full min-h-0 overflow-hidden rounded-xl border border-slate-700/70 bg-slate-900/55">
      <div className="h-full overflow-auto">
        <table className="min-w-full border-separate border-spacing-0 text-sm">
          <thead className="sticky top-0 z-20 bg-slate-900/95 text-xs uppercase tracking-[0.12em] text-slate-400">
            <tr>
              <th className="px-3 py-3 text-left">Attack / Prompt</th>
              <th className="px-3 py-3 text-left">Category</th>
              <th className="px-3 py-3 text-left">Severity</th>
              <th className="px-3 py-3 text-left">Target</th>
              <th className="px-3 py-3 text-left">Outcome</th>
              <th className="px-3 py-3 text-left">Execution</th>
              <th className="px-3 py-3 text-left">Signals</th>
              <th className="px-3 py-3 text-left">Response Preview</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-700/60">
            {rows.map((row) => {
              const selected = selectedAttackId === row.attackId;
              return (
                <tr
                  key={row.attackId}
                  onClick={() => onSelectRow(row.attackId)}
                  className={`cursor-pointer transition ${
                    selected
                      ? "bg-cyan-500/12 ring-1 ring-inset ring-cyan-300/45"
                      : "hover:bg-slate-800/65"
                  }`}
                >
                  <td className="px-3 py-3">
                    <p className="font-mono text-xs font-semibold text-cyan-200">{row.attackId}</p>
                    <p className="line-clamp-1 text-xs text-slate-400">{row.attackName}</p>
                  </td>
                  <td className="px-3 py-3 text-slate-300">{formatCategory(row.category)}</td>
                  <td className="px-3 py-3 text-slate-300">{formatSeverity(row.severity)}</td>
                  <td className="px-3 py-3 text-slate-300">{row.targetName}</td>
                  <td className="px-3 py-3">
                    <ClassificationBadge classification={row.classification} />
                  </td>
                  <td className="px-3 py-3 text-slate-300">{row.executionStatus}</td>
                  <td className="px-3 py-3 text-slate-300">
                    <div className="flex gap-1.5 text-[11px]">
                      <span className="rounded-full bg-amber-500/15 px-2 py-0.5 text-amber-200">
                        W:{row.warningsCount}
                      </span>
                      <span className="rounded-full bg-rose-500/15 px-2 py-0.5 text-rose-200">
                        F:{row.flagsCount}
                      </span>
                    </div>
                  </td>
                  <td className="px-3 py-3 text-xs text-slate-400">{row.responsePreview}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
