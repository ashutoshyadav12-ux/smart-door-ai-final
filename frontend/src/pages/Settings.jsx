import { useEffect, useState } from "react";
import api from "../api/client.js";

const FIELDS = [
  { k: "match_threshold", label: "Match threshold (cosine)", type: "range", min: 0.2, max: 0.9, step: 0.01, hint: "Higher = stricter. 0.45 is a good start." },
  { k: "unlock_duration", label: "Unlock duration (seconds)", type: "number", min: 1, max: 60 },
  { k: "liveness_required", label: "Require liveness check (prototype)", type: "bool" },
  { k: "max_failed_attempts", label: "Failed attempts before lockout", type: "number", min: 1, max: 20 },
  { k: "lockout_seconds", label: "Lockout duration (seconds)", type: "number", min: 5, max: 3600 },
  { k: "cooldown_seconds", label: "Per-person cooldown (seconds)", type: "number", min: 0, max: 60 },
];

export default function Settings() {
  const [s, setS] = useState(null);
  const [msg, setMsg] = useState("");
  useEffect(() => { api.get("/settings").then((r) => setS(r.data)); }, []);
  if (!s) return <div className="text-slate-400">Loading…</div>;

  const save = async () => {
    try { setS((await api.put("/settings", s)).data); setMsg("Saved ✔"); }
    catch { setMsg("Save failed"); }
    setTimeout(() => setMsg(""), 2500);
  };

  return (
    <div className="max-w-xl space-y-4">
      <h2 className="text-xl font-semibold">Settings</h2>
      <div className="card space-y-5">
        {FIELDS.map((f) => (
          <div key={f.k}>
            <label className="mb-1 block text-sm">{f.label}{f.type === "range" && <span className="ml-2 text-indigo-400">{Number(s[f.k]).toFixed(2)}</span>}</label>
            {f.type === "bool" ? (
              <input type="checkbox" checked={!!s[f.k]} onChange={(e) => setS({ ...s, [f.k]: e.target.checked })} />
            ) : (
              <input className={f.type === "range" ? "w-full" : "input"} type={f.type} min={f.min} max={f.max} step={f.step}
                value={s[f.k]} onChange={(e) => setS({ ...s, [f.k]: Number(e.target.value) })} />
            )}
            {f.hint && <div className="mt-1 text-xs text-slate-500">{f.hint}</div>}
          </div>
        ))}
        <div className="flex items-center gap-3">
          <button className="btn-primary" onClick={save}>Save settings</button>
          <span className="text-sm text-emerald-400">{msg}</span>
        </div>
      </div>
    </div>
  );
}
