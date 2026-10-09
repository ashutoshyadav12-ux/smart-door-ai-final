import LiveDoorIndicator from "../components/LiveDoorIndicator.jsx";
import MetricCard from "../components/MetricCard.jsx";
import StatusBadge from "../components/StatusBadge.jsx";
import usePoll from "../hooks/usePoll.js";

export default function Dashboard() {
  const { data: s, error } = usePoll("/dashboard/stats", 3000);
  return (
    <div className="space-y-5">
      <h2 className="text-xl font-semibold">Dashboard</h2>
      {error && <div className="text-sm text-rose-400">Backend unreachable.</div>}
      <LiveDoorIndicator door={s?.door} />
      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        <MetricCard label="People" value={s?.people} hint={`${s?.enrolled_people ?? 0} with face enrolled`} />
        <MetricCard label="Granted (24h)" value={s?.granted_24h} />
        <MetricCard label="Denied (24h)" value={s?.denied_24h} />
        <MetricCard label="Devices online" value={s?.devices_online} />
      </div>
      <div className="card">
        <h3 className="mb-3 font-medium">Recent activity</h3>
        <table className="w-full">
          <thead><tr><th className="th">Time</th><th className="th">Person</th><th className="th">Event</th><th className="th">Conf.</th></tr></thead>
          <tbody>
            {s?.recent?.map((l) => (
              <tr key={l.id} className="border-t border-slate-800">
                <td className="td">{new Date(l.timestamp).toLocaleString()}</td>
                <td className="td">{l.person_name || "—"}</td>
                <td className="td"><StatusBadge status={l.event_type} /></td>
                <td className="td">{l.confidence != null ? l.confidence.toFixed(2) : "—"}</td>
              </tr>
            ))}
            {s && !s.recent.length && <tr><td className="td text-slate-500" colSpan={4}>No events yet.</td></tr>}
          </tbody>
        </table>
      </div>
    </div>
  );
}
