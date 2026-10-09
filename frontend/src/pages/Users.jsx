import { useCallback, useEffect, useState } from "react";
import { Link } from "react-router-dom";
import Modal from "../components/Modal.jsx";
import StatusBadge from "../components/StatusBadge.jsx";
import api from "../api/client.js";

export default function Users() {
  const [rows, setRows] = useState([]);
  const [open, setOpen] = useState(false);
  const [name, setName] = useState("");
  const [role, setRole] = useState("resident");

  const load = useCallback(() => api.get("/users").then((r) => setRows(r.data.results ?? r.data)), []);
  useEffect(() => { load(); }, [load]);

  const create = async () => {
    await api.post("/users", { full_name: name, role });
    setName(""); setOpen(false); load();
  };
  const toggle = async (u) => {
    await api.patch(`/users/${u.id}`, { status: u.status === "active" ? "disabled" : "active" });
    load();
  };
  const remove = async (u) => {
    if (confirm(`Delete ${u.full_name} and all face data?`)) { await api.delete(`/users/${u.id}`); load(); }
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold">Users</h2>
        <button className="btn-primary" onClick={() => setOpen(true)}>+ Add user</button>
      </div>
      <div className="card overflow-x-auto p-0">
        <table className="w-full">
          <thead><tr><th className="th">Name</th><th className="th">Role</th><th className="th">Status</th><th className="th">Face samples</th><th className="th"></th></tr></thead>
          <tbody>
            {rows.map((u) => (
              <tr key={u.id} className="border-t border-slate-800">
                <td className="td">{u.full_name}</td>
                <td className="td capitalize">{u.role}</td>
                <td className="td"><StatusBadge status={u.status} /></td>
                <td className="td">{u.face_samples}</td>
                <td className="td space-x-2 text-right">
                  <Link className="btn-ghost inline-block" to={`/enroll?person=${u.id}`}>Enroll</Link>
                  <button className="btn-ghost" onClick={() => toggle(u)}>{u.status === "active" ? "Disable" : "Enable"}</button>
                  <button className="btn-danger" onClick={() => remove(u)}>Delete</button>
                </td>
              </tr>
            ))}
            {!rows.length && <tr><td className="td text-slate-500" colSpan={5}>No users yet.</td></tr>}
          </tbody>
        </table>
      </div>
      <Modal open={open} title="Add user" onClose={() => setOpen(false)}>
        <div className="space-y-3">
          <input className="input" placeholder="Full name" value={name} onChange={(e) => setName(e.target.value)} />
          <select className="input" value={role} onChange={(e) => setRole(e.target.value)}>
            <option value="resident">Resident</option><option value="guest">Guest</option><option value="admin">Admin</option>
          </select>
          <button className="btn-primary w-full" disabled={!name.trim()} onClick={create}>Create</button>
        </div>
      </Modal>
    </div>
  );
}
