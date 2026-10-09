const COLORS = {
  GRANTED: "bg-emerald-500/15 text-emerald-300",
  MANUAL_UNLOCK: "bg-emerald-500/15 text-emerald-300",
  unlocked: "bg-emerald-500/15 text-emerald-300",
  online: "bg-emerald-500/15 text-emerald-300",
  active: "bg-emerald-500/15 text-emerald-300",
  UNKNOWN: "bg-amber-500/15 text-amber-300",
  LIVENESS_FAIL: "bg-amber-500/15 text-amber-300",
  DENIED: "bg-rose-500/15 text-rose-300",
  LOCKOUT: "bg-rose-500/15 text-rose-300",
  disabled: "bg-rose-500/15 text-rose-300",
  offline: "bg-rose-500/15 text-rose-300",
  locked: "bg-slate-500/20 text-slate-300",
  MANUAL_LOCK: "bg-slate-500/20 text-slate-300",
};

export default function StatusBadge({ status }) {
  return (
    <span className={`rounded-full px-2.5 py-0.5 text-xs font-medium ${COLORS[status] || "bg-slate-700 text-slate-200"}`}>
      {String(status).replace("_", " ")}
    </span>
  );
}
