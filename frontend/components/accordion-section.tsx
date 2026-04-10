import { AnimatePresence, motion } from "framer-motion";

interface AccordionSectionProps {
  title: string;
  subtitle?: string;
  open: boolean;
  onToggle: () => void;
  children: React.ReactNode;
}

export function AccordionSection({ title, subtitle, open, onToggle, children }: AccordionSectionProps) {
  return (
    <section className="rounded-xl border border-slate-700/70 bg-slate-900/60">
      <button
        type="button"
        onClick={onToggle}
        className="flex w-full items-center justify-between gap-3 px-3 py-2.5 text-left"
      >
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.12em] text-slate-200">{title}</p>
          {subtitle && <p className="mt-0.5 text-[11px] text-slate-400">{subtitle}</p>}
        </div>
        <span className="text-xs text-slate-400">{open ? "Collapse" : "Expand"}</span>
      </button>

      <AnimatePresence initial={false}>
        {open && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2, ease: "easeInOut" }}
            className="overflow-hidden"
          >
            <div className="border-t border-slate-700/60 px-3 py-3">{children}</div>
          </motion.div>
        )}
      </AnimatePresence>
    </section>
  );
}
