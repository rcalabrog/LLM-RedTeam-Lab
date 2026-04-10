import { motion } from "framer-motion";

export function LabHeader() {
  return (
    <motion.header
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.35 }}
      className="rounded-2xl border border-slate-700/70 bg-slate-900/55 p-5 shadow-[0_25px_60px_-25px_rgba(2,6,23,0.85)] backdrop-blur"
    >
      <p className="font-mono text-xs uppercase tracking-[0.16em] text-cyan-300">LLM Security Lab</p>
      <h1 className="mt-2 text-2xl font-semibold text-slate-100">LLM Red Team Lab</h1>
      <p className="mt-2 max-w-4xl text-sm text-slate-300">
        Local-first offensive testing workspace for comparing vulnerable and defended LLM target behavior across
        deterministic attack campaigns.
      </p>
    </motion.header>
  );
}
