import { useMemo, useState } from "react";

import { AccordionSection } from "@/components/accordion-section";
import { ClassificationBadge } from "@/components/classification-badge";
import { formatCategory, formatRate, formatSeverity } from "@/lib/presenters";
import { AttackResultRow, CampaignViewModel } from "@/types/ui";

interface InspectorPanelProps {
  view: CampaignViewModel | null;
  selectedRow: AttackResultRow | null;
}

type SectionKey = "overview" | "category" | "severity" | "detail" | "execution";

function stringifyMetadata(value: unknown): string {
  if (value == null) {
    return "n/a";
  }
  try {
    return JSON.stringify(value, null, 2);
  } catch {
    return String(value);
  }
}

export function InspectorPanel({ view, selectedRow }: InspectorPanelProps) {
  const [openSections, setOpenSections] = useState<Record<SectionKey, boolean>>({
    overview: true,
    category: false,
    severity: false,
    detail: true,
    execution: false
  });

  const summary = view?.evaluated.summary ?? null;

  const cards = useMemo(() => {
    if (!summary) {
      return [];
    }
    return [
      { label: "Offensive Success", value: summary.success_count, tone: "text-rose-200" },
      { label: "Defended / Failed", value: summary.failed_count, tone: "text-emerald-200" },
      { label: "Ambiguous", value: summary.ambiguous_count, tone: "text-amber-200" }
    ];
  }, [summary]);

  return (
    <section className="flex h-full min-h-0 flex-col rounded-2xl border border-slate-700/70 bg-slate-900/60 p-3 backdrop-blur">
      <header className="shrink-0 border-b border-slate-700/60 pb-2">
        <p className="text-xs uppercase tracking-[0.14em] text-slate-300">Inspector</p>
        <p className="mt-1 text-xs text-slate-400">
          {selectedRow ? `Selected: ${selectedRow.attackId}` : "Select an attack row for deep inspection."}
        </p>
      </header>

      <div className="mt-3 min-h-0 flex-1 space-y-2 overflow-y-auto pr-1">
        <AccordionSection
          title="Overview Metrics"
          subtitle={summary ? `${summary.total_attacks} evaluated attacks` : "No campaign loaded"}
          open={openSections.overview}
          onToggle={() =>
            setOpenSections((current) => ({ ...current, overview: !current.overview }))
          }
        >
          {!summary ? (
            <p className="text-sm text-slate-300">Run a campaign to view aggregate metrics.</p>
          ) : (
            <div className="space-y-2">
              <div className="grid gap-2">
                {cards.map((card) => (
                  <div key={card.label} className="rounded-lg bg-slate-800/55 px-2 py-2">
                    <div className="flex items-end justify-between gap-2">
                      <div>
                        <p className="text-[11px] uppercase tracking-[0.12em] text-slate-400">{card.label}</p>
                        <p className={`text-lg font-semibold ${card.tone}`}>{card.value}</p>
                      </div>
                      {summary.total_attacks > 0 && (
                        <p className="text-[11px] text-slate-400">
                          {formatRate(card.value / summary.total_attacks)}
                        </p>
                      )}
                    </div>
                  </div>
                ))}
              </div>
              <div className="text-xs text-slate-300">
                <p>Success rate: {formatRate(summary.success_rate_overall)}</p>
                <p>Failed rate: {formatRate(summary.failed_rate_overall)}</p>
                <p>Ambiguous rate: {formatRate(summary.ambiguous_rate_overall)}</p>
              </div>
            </div>
          )}
        </AccordionSection>

        <AccordionSection
          title="Category Breakdown"
          open={openSections.category}
          onToggle={() =>
            setOpenSections((current) => ({ ...current, category: !current.category }))
          }
        >
          {!summary ? (
            <p className="text-sm text-slate-300">No category data yet.</p>
          ) : (
            <div className="space-y-2">
              {summary.per_category.map((item) => (
                <div key={item.category} className="rounded-lg bg-slate-800/55 px-2 py-2 text-xs">
                  <div className="flex items-center justify-between">
                    <span className="text-slate-200">{formatCategory(item.category)}</span>
                    <span className="text-slate-400">{formatRate(item.success_rate)}</span>
                  </div>
                  <p className="mt-1 text-slate-400">
                    S:{item.success} F:{item.failed} A:{item.ambiguous} / {item.total}
                  </p>
                </div>
              ))}
            </div>
          )}
        </AccordionSection>

        <AccordionSection
          title="Severity Breakdown"
          open={openSections.severity}
          onToggle={() =>
            setOpenSections((current) => ({ ...current, severity: !current.severity }))
          }
        >
          {!summary ? (
            <p className="text-sm text-slate-300">No severity data yet.</p>
          ) : (
            <div className="space-y-1 text-xs text-slate-300">
              {summary.per_severity.map((item) => (
                <p key={item.severity}>
                  {formatSeverity(item.severity)}: {item.success}/{item.total} success
                </p>
              ))}
            </div>
          )}
        </AccordionSection>

        <AccordionSection
          title="Selected Attack Detail"
          subtitle={selectedRow ? selectedRow.attackName : "No row selected"}
          open={openSections.detail}
          onToggle={() => setOpenSections((current) => ({ ...current, detail: !current.detail }))}
        >
          {!selectedRow ? (
            <p className="text-sm text-slate-300">Select a row in Campaign Results.</p>
          ) : (
            <div className="space-y-3">
              <div className="rounded-lg border border-cyan-400/25 bg-cyan-500/5 p-2">
                <p className="font-mono text-xs text-cyan-200">{selectedRow.attackId}</p>
                <p className="mt-1 text-sm font-semibold text-slate-100">{selectedRow.attackName}</p>
              </div>

              <div className="flex flex-wrap items-center gap-2">
                <ClassificationBadge classification={selectedRow.classification} />
                <span className="rounded-full bg-slate-800/70 px-2 py-1 text-xs text-slate-300">
                  {formatCategory(selectedRow.category)}
                </span>
                <span className="rounded-full bg-slate-800/70 px-2 py-1 text-xs text-slate-300">
                  {formatSeverity(selectedRow.severity)}
                </span>
              </div>

              <div className="rounded-lg bg-slate-800/55 p-2">
                <p className="text-[11px] uppercase tracking-[0.12em] text-slate-400">Reasoning Summary</p>
                <p className="mt-1 text-sm text-slate-200">{selectedRow.reasoningSummary}</p>
              </div>

              <div className="rounded-lg bg-slate-800/55 p-2">
                <p className="text-[11px] uppercase tracking-[0.12em] text-slate-400">Matched Signals</p>
                <div className="mt-1 flex flex-wrap gap-1.5">
                  {selectedRow.matchedSignals.length === 0 && (
                    <span className="text-xs text-slate-400">None</span>
                  )}
                  {selectedRow.matchedSignals.map((signal) => (
                    <span key={signal} className="rounded-full bg-slate-700/70 px-2 py-1 text-xs text-slate-200">
                      {signal}
                    </span>
                  ))}
                </div>
              </div>

              <div className="rounded-lg bg-slate-800/55 p-2">
                <p className="text-[11px] uppercase tracking-[0.12em] text-slate-400">Matched Rules</p>
                <div className="mt-1 space-y-1.5">
                  {selectedRow.matchedRules.length === 0 && (
                    <span className="text-xs text-slate-400">None</span>
                  )}
                  {selectedRow.matchedRules.map((rule) => (
                    <div key={rule.rule_id} className="rounded-md bg-slate-900/70 p-1.5">
                      <p className="text-xs font-semibold text-slate-200">{rule.rule_id}</p>
                      <p className="mt-0.5 text-xs text-slate-400">{rule.evidence}</p>
                    </div>
                  ))}
                </div>
              </div>

              <div className="rounded-lg bg-slate-800/55 p-2">
                <p className="text-[11px] uppercase tracking-[0.12em] text-slate-400">Response Excerpt</p>
                <p className="mt-1 max-h-32 overflow-auto text-sm text-slate-200">
                  {selectedRow.responseExcerpt ?? "No excerpt available."}
                </p>
              </div>
            </div>
          )}
        </AccordionSection>

        <AccordionSection
          title="Execution Snapshot / Raw Metadata"
          open={openSections.execution}
          onToggle={() =>
            setOpenSections((current) => ({ ...current, execution: !current.execution }))
          }
        >
          {!selectedRow ? (
            <p className="text-sm text-slate-300">No execution metadata yet.</p>
          ) : (
            <div className="space-y-2 text-xs text-slate-300">
              <p>Execution status: {selectedRow.executionStatus}</p>
              <p>Warnings: {selectedRow.warningsCount}</p>
              <p>Flags: {selectedRow.flagsCount}</p>
              <p>Defense mode: {selectedRow.rawResult?.defense_mode ?? "n/a"}</p>
              <p>Risk level: {selectedRow.rawResult?.execution_metadata.risk_level ?? "n/a"}</p>
              <pre className="max-h-44 overflow-auto rounded-lg bg-slate-950/75 p-2 text-[11px] text-slate-300">
                {stringifyMetadata(selectedRow.rawResult?.execution_metadata.raw_target_metadata)}
              </pre>
            </div>
          )}
        </AccordionSection>
      </div>
    </section>
  );
}
