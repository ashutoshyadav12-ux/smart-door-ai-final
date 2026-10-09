export default function LiveDoorIndicator({ door }) {
  if (!door) return <div className="card text-slate-400">Loading door…</div>;
  const open = door.state === "unlocked";
  return (
    <div className={`card flex items-center gap-4 ${open ? "border-emerald-600" : ""}`}>
      <div className={`flex h-14 w-14 items-center justify-center rounded-full text-2xl ${open ? "bg-emerald-500/20" : "bg-slate-800"}`}>
        {open ? "🔓" : "🔒"}
      </div>
      <div>
        <div className="text-lg font-semibold capitalize">{door.state}</div>
        <div className="text-xs text-slate-400">
          {door.mode} mode · {door.device_id} · {door.connection}
          {open && door.seconds_remaining ? ` · relock in ${Math.ceil(door.seconds_remaining)}s` : ""}
        </div>
      </div>
    </div>
  );
}
