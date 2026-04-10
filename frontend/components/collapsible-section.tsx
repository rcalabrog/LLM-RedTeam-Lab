import { AnimatePresence, motion } from "framer-motion";

interface CollapsibleSectionProps {
  title: string;
  subtitle?: string;
  open: boolean;
  onToggle: () => void;
  children: React.ReactNode;
  fill?: boolean;
  className?: string;
  contentClassName?: string;
}

export function CollapsibleSection({
  title,
  subtitle,
  open,
  onToggle,
  children,
  fill = false,
  className,
  contentClassName
}: CollapsibleSectionProps) {
  return (
    <section
      className={`rounded-xl border border-slate-700/70 bg-slate-900/60 ${fill ? "min-h-0 flex flex-1 flex-col overflow-hidden" : ""} ${
        className ?? ""
      }`}
    >
      <button
        type="button"
        onClick={onToggle}
        className="flex w-full items-center justify-between gap-3 px-3 py-2.5 text-left"
      >
        <div className="min-w-0">
          <p className="text-xs font-semibold uppercase tracking-[0.12em] text-slate-200">{title}</p>
          {subtitle && <p className="mt-0.5 truncate text-[11px] text-slate-400">{subtitle}</p>}
        </div>
        <span className="shrink-0 text-xs text-slate-400">{open ? "Collapse" : "Expand"}</span>
      </button>

      {fill ? (
        open ? (
          <div className={`min-h-0 flex-1 border-t border-slate-700/60 ${contentClassName ?? "p-2.5"}`}>{children}</div>
        ) : null
      ) : (
        <AnimatePresence initial={false}>
          {open && (
            <motion.div
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: "auto", opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              transition={{ duration: 0.2, ease: "easeInOut" }}
              className="overflow-hidden"
            >
              <div className={`border-t border-slate-700/60 ${contentClassName ?? "p-2.5"}`}>{children}</div>
            </motion.div>
          )}
        </AnimatePresence>
      )}
    </section>
  );
}

