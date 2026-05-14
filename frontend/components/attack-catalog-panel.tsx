import { useMemo, useState } from "react";

import { AccordionSection } from "@/components/accordion-section";
import { formatCategory, formatSeverity } from "@/lib/presenters";
import { AttackCategory, AttackDefinition } from "@/types/api";

const categoryOrder: AttackCategory[] = [
  "data_leakage_simulation",
  "jailbreak_basic",
  "policy_bypass",
  "prompt_injection_direct",
  "system_prompt_extraction"
];

interface AttackCatalogPanelProps {
  attacks: AttackDefinition[];
  loading: boolean;
  error: string | null;
}

function groupedAttacks(attacks: AttackDefinition[]): Record<AttackCategory, AttackDefinition[]> {
  return categoryOrder.reduce((groups, category) => {
    groups[category] = attacks.filter((attack) => attack.category === category);
    return groups;
  }, {} as Record<AttackCategory, AttackDefinition[]>);
}

export function AttackCatalogPanel({ attacks, loading, error }: AttackCatalogPanelProps) {
  const [openCategories, setOpenCategories] = useState<Record<AttackCategory, boolean>>({
    data_leakage_simulation: true,
    jailbreak_basic: false,
    policy_bypass: false,
    prompt_injection_direct: false,
    system_prompt_extraction: false
  });
  const groups = useMemo(() => groupedAttacks(attacks), [attacks]);

  return (
    <section className="flex h-full min-h-0 flex-col rounded-2xl border border-slate-700/70 bg-slate-900/60 p-3 backdrop-blur">
      <header className="shrink-0 border-b border-slate-700/60 pb-2">
        <div className="flex items-start justify-between gap-3">
          <div>
            <h2 className="text-sm font-semibold uppercase tracking-[0.12em] text-slate-200">
              Attack Catalog
            </h2>
            <p className="mt-1 text-xs text-slate-400">
              Inspect prompts and metadata before launching a campaign.
            </p>
          </div>
          <span className="shrink-0 rounded-full bg-slate-800/80 px-2 py-1 text-[11px] text-cyan-200">
            {attacks.length} prompts
          </span>
        </div>
      </header>

      <div className="mt-3 min-h-0 flex-1 space-y-2 overflow-y-auto pr-1">
        {loading && <p className="rounded-lg bg-slate-900/60 p-3 text-xs text-slate-300">Loading attack prompts...</p>}
        {error && <p className="rounded-lg bg-rose-500/10 p-3 text-xs text-rose-200">{error}</p>}

        {!loading &&
          !error &&
          categoryOrder.map((category) => {
            const categoryAttacks = groups[category];
            return (
              <AccordionSection
                key={category}
                title={formatCategory(category)}
                subtitle={`${categoryAttacks.length} prompts`}
                open={openCategories[category]}
                onToggle={() =>
                  setOpenCategories((current) => ({ ...current, [category]: !current[category] }))
                }
              >
                {categoryAttacks.length === 0 ? (
                  <p className="text-xs text-slate-400">No prompts available in this category.</p>
                ) : (
                  <div className="space-y-2">
                    {categoryAttacks.map((attack) => (
                      <article
                        key={attack.attack_id}
                        className="rounded-lg border border-slate-700/70 bg-slate-950/35 p-2.5"
                      >
                        <div className="flex items-start justify-between gap-2">
                          <div className="min-w-0">
                            <p className="truncate font-mono text-[11px] text-cyan-200">{attack.attack_id}</p>
                            <h3 className="mt-0.5 text-sm font-semibold text-slate-100">{attack.name}</h3>
                          </div>
                          <span className="shrink-0 rounded-full bg-slate-800/80 px-2 py-0.5 text-[11px] text-slate-300">
                            {formatSeverity(attack.severity)}
                          </span>
                        </div>
                        <p className="mt-2 text-xs leading-5 text-slate-300">{attack.description}</p>
                        <details className="mt-2 rounded-lg bg-slate-900/70">
                          <summary className="cursor-pointer px-2 py-1.5 text-[11px] font-semibold uppercase tracking-[0.1em] text-slate-400">
                            Prompt
                          </summary>
                          <pre className="max-h-40 overflow-auto whitespace-pre-wrap break-words border-t border-slate-700/60 px-2 py-2 text-xs leading-5 text-slate-200">
                            {attack.prompt}
                          </pre>
                        </details>
                        {(attack.tags.length > 0 || attack.expected_risk_signals.length > 0) && (
                          <div className="mt-2 flex flex-wrap gap-1.5">
                            {attack.tags.slice(0, 4).map((tag) => (
                              <span key={tag} className="rounded-full bg-slate-800/80 px-2 py-0.5 text-[10px] text-slate-300">
                                {tag}
                              </span>
                            ))}
                            {attack.expected_risk_signals.slice(0, 3).map((signal) => (
                              <span key={signal} className="rounded-full bg-amber-500/15 px-2 py-0.5 text-[10px] text-amber-200">
                                {signal}
                              </span>
                            ))}
                          </div>
                        )}
                      </article>
                    ))}
                  </div>
                )}
              </AccordionSection>
            );
          })}
      </div>
    </section>
  );
}
