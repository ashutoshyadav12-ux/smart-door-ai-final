import { useState } from "react";
import LiveDoorIndicator from "../components/LiveDoorIndicator.jsx";
import StatusBadge from "../components/StatusBadge.jsx";
import api from "../api/client.js";
import usePoll from "../hooks/usePoll.js";

export default function IoTDevices() {
  const { data: door } = usePoll("/door/status", 1500);
  const { data: devices } = usePoll("/iot/devices", 4000);
  const [busy, setBusy] = useState(false);

  const cmd = async (action) => {
    setBusy(true);
    try { await api.post("/iot/command", { action }); } finally { setBusy(false); }
  };

  return (
    <div className="space-y-4">
      <h2 className="text-xl font-semibold">IoT Devices</h2>
      <LiveDoorIndicator door={door} />
      <div className="flex gap-3">
        <button className="btn-primary" disabled={busy} onClick={() => cmd("unlock")}>🔓 Unlock</button>
        <button className="btn-ghost" disabled={busy} onClick={() => cmd("lock")}>🔒 Lock</button>
      </div>
      <div className="card overflow-x-auto p-0">
        <table className="w-full">
          <thead><tr><th className="th">Device</th><th className="th">Status</th><th className="th">Door</th><th className="th">Firmware</th><th className="th">Last heartbeat</th></tr></thead>
          <tbody>
            {(devices || []).map((d) => (
              <tr key={d.id} className="border-t border-slate-800">
                <td className="td">{d.name || d.device_id}<div className="text-xs text-slate-500">{d.device_id}</div></td>
                <td className="td"><StatusBadge status={d.connection_status} /></td>
                <td className="td"><StatusBadge status={d.door_state} /></td>
                <td className="td">{d.firmware || "—"}</td>
                <td className="td">{d.last_heartbeat ? new Date(d.last_heartbeat).toLocaleString() : "—"}</td>
              </tr>
            ))}
            {devices && !devices.length && <tr><td className="td text-slate-500" colSpan={5}>No devices have reported in yet (demo mode uses a virtual door).</td></tr>}
          </tbody>
        </table>
      </div>
    </div>
  );
}
