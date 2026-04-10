import { ReadinessResponse } from "@/types/api";

interface ReadinessIndicatorProps {
  readiness: ReadinessResponse | null;
  loading: boolean;
}

function statusClass(status: string): string {
  if (status === "ok") {
    return "bg-emerald-500/20 text-emerald-200 ring-1 ring-emerald-400/40";
  }
  return "bg-amber-500/20 text-amber-100 ring-1 ring-amber-400/40";
}

function componentDotClass(status: string): string {
  return status === "ok" ? "bg-emerald-300" : "bg-amber-300";
}

export function ReadinessIndicator({ readiness, loading }: ReadinessIndicatorProps) {
  if (loading) {
    return (
      <div className="rounded-lg bg-slate-900/50 px-3 py-2 text-xs text-slate-300 ring-1 ring-slate-700/60">
        Checking local runtime readiness...
      </div>
    );
  }

  if (!readiness) {
    return (
      <div className="rounded-lg bg-slate-900/50 px-3 py-2 text-xs text-slate-300 ring-1 ring-slate-700/60">
        Readiness unavailable.
      </div>
    );
  }

  return (
    <div className="space-y-2 rounded-xl bg-slate-900/70 p-3 ring-1 ring-slate-700/70">
      <div className="flex items-center justify-between">
        <p className="text-xs font-medium uppercase tracking-[0.14em] text-slate-300">Readiness</p>
        <span className={`rounded-full px-2 py-1 text-[11px] font-semibold ${statusClass(readiness.status)}`}>
          {readiness.status}
        </span>
      </div>
      <div className="space-y-1.5">
        {readiness.components.map((component) => (
          <div key={component.name} className="rounded-md bg-slate-800/55 px-2 py-1.5 text-xs">
            <div className="flex items-center justify-between">
              <span className="flex items-center gap-1.5 text-slate-300">
                <span className={`h-1.5 w-1.5 rounded-full ${componentDotClass(component.status)}`} />
                {component.name}
              </span>
              <span className={component.status === "ok" ? "text-emerald-300" : "text-amber-300"}>
                {component.status}
              </span>
            </div>
            {component.detail && (
              <p className="mt-1 line-clamp-2 text-[11px] text-slate-500">{component.detail}</p>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
