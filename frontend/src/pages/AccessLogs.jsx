import { useEffect, useState } from "react";
import StatusBadge from "../components/StatusBadge.jsx";
import api from "../api/client.js";

const EVENTS = ["", "GRANTED", "UNKNOWN", "DENIED", "LIVENESS_FAIL", "LOCKOUT", "MANUAL_UNLOCK", "MANUAL_LOCK"];

export default function AccessLogs() {
  const [f, setF] = useState({ event_type: "", q: "", date_from: "", date_to: "" });
  const [page, setPage] = useState(1);
  const [data, setData] = useState({ results: [], count: 0, next: null, previous: null });

  useEffect(() => {
    const params = { page, ...Object.fromEntries(Object.entries(f).filter(([, v]) => v)) };
    api.get("/access-logs", { params }).then((r) => setData(r.data));
  }, [f, page]);

  const set = (k) => (e) => { setPage(1); setF({ ...f, [k]: e.target.value }); };

  return (
    <div className="space-y-4">
      <h2 className="text-xl font-semibold">Access Logs</h2>
      <div className="card grid gap-3 md:grid-cols-4">
        <select className="input" value={f.event_type} onChange={set("event_type")}>{EVENTS.map((e) => <option key={e} value={e}>{e || "All events"}</option>)}</select>
        <input className="input" placeholder="Search person…" value={f.q} onChange={set("q")} />
        <input className="input" type="date" value={f.date_from} onChange={set("date_from")} />
        <input className="input" type="date" value={f.date_to} onChange={set("date_to")} />
      </div>
      <div className="card overflow-x-auto p-0">
        <table className="w-full">
          <thead><tr><th className="th">Time</th><th className="th">Person</th><th className="th">Event</th><th className="th">Conf.</th><th className="th">Device</th><th className="th">Detail</th></tr></thead>
          <tbody>
            {data.results.map((l) => (
              <tr key={l.id} className="border-t border-slate-800">
                <td className="td whitespace-nowrap">{new Date(l.timestamp).toLocaleString()}</td>
                <td className="td">{l.person_name || "—"}</td>
                <td className="td"><StatusBadge status={l.event_type} /></td>
                <td className="td">{l.confidence != null ? l.confidence.toFixed(2) : "—"}</td>
                <td className="td">{l.device}</td>
                <td className="td text-slate-400">{l.detail}</td>
              </tr>
            ))}
            {!data.results.length && <tr><td className="td text-slate-500" colSpan={6}>No matching events.</td></tr>}
          </tbody>
        </table>
      </div>
      <div className="flex items-center justify-between text-sm text-slate-400">
        <span>{data.count} events</span>
        <div className="space-x-2">
          <button className="btn-ghost" disabled={!data.previous} onClick={() => setPage(page - 1)}>Prev</button>
          <button className="btn-ghost" disabled={!data.next} onClick={() => setPage(page + 1)}>Next</button>
        </div>
      </div>
    </div>
  );
}
