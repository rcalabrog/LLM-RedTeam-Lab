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
      <div className="rounded-xl border border-slate-700/70 bg-slate-900/60 p-6 text-sm text-slate-300">
        No attack rows available yet.
      </div>
    );
  }

  return (
    <div className="overflow-x-auto rounded-2xl border border-slate-700/70 bg-slate-900/55">
      <table className="min-w-full divide-y divide-slate-700/60 text-sm">
        <thead className="bg-slate-900/80 text-xs uppercase tracking-[0.12em] text-slate-400">
          <tr>
            <th className="px-3 py-3 text-left">Attack</th>
            <th className="px-3 py-3 text-left">Category</th>
            <th className="px-3 py-3 text-left">Severity</th>
            <th className="px-3 py-3 text-left">Target</th>
            <th className="px-3 py-3 text-left">Classification</th>
            <th className="px-3 py-3 text-left">Execution</th>
            <th className="px-3 py-3 text-left">Warn / Flags</th>
            <th className="px-3 py-3 text-left">Preview</th>
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
                  selected ? "bg-cyan-400/10" : "hover:bg-slate-800/50"
                }`}
              >
                <td className="px-3 py-3">
                  <p className="font-semibold text-slate-100">{row.attackId}</p>
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
                  {row.warningsCount} / {row.flagsCount}
                </td>
                <td className="px-3 py-3 text-xs text-slate-400">{row.responsePreview}</td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
