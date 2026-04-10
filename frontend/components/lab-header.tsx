import { motion } from "framer-motion";
import Image from "next/image";

interface LabHeaderProps {
  compact?: boolean;
}

export function LabHeader({ compact = false }: LabHeaderProps) {
  return (
    <motion.header
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.35 }}
      className={`rounded-2xl border border-slate-700/70 bg-slate-900/55 shadow-[0_25px_60px_-25px_rgba(2,6,23,0.85)] backdrop-blur ${
        compact ? "p-4" : "p-5"
      }`}
    >
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="font-mono text-xs uppercase tracking-[0.16em] text-cyan-300">
            LLM Security Lab
          </p>
          <h1
            className={`mt-2 font-semibold text-slate-100 ${compact ? "text-xl" : "text-2xl"}`}
          >
            Red Team Lab
          </h1>
          <p
            className={`mt-2 max-w-4xl text-slate-300 ${compact ? "text-xs" : "text-sm"}`}
          >
            Offensive testing workspace for comparing vulnerable and defended LLM
            target behavior across deterministic attack campaigns.
          </p>
        </div>

        <a
          href="https://github.com/rcalabrog"
          target="_blank"
          rel="noopener noreferrer"
          aria-label="Open rcalabrog GitHub profile"
          className="shrink-0 rounded-lg border border-slate-700/60 bg-slate-900/55 p-1 transition hover:border-cyan-300/60 hover:bg-slate-800/70"
        >
          <Image
            src="/images/rc_logo.png"
            alt="RC logo"
            width={compact ? 52 : 62}
            height={compact ? 52 : 62}
            className="h-auto w-auto"
            priority
          />
        </a>
      </div>
    </motion.header>
  );
}
