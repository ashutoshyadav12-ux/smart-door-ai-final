import { useState } from "react";
import { Navigate, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext.jsx";

export default function Login() {
  const { token, login } = useAuth();
  const nav = useNavigate();
  const [u, setU] = useState("");
  const [p, setP] = useState("");
  const [err, setErr] = useState("");
  const [busy, setBusy] = useState(false);

  if (token) return <Navigate to="/" replace />;

  const submit = async (e) => {
    e.preventDefault();
    setBusy(true);
    setErr("");
    try {
      await login(u, p);
      nav("/");
    } catch (e2) {
      setErr(e2.response ? "Invalid username or password" : "Cannot reach backend (check VITE_API_URL / CORS)");
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center p-4">
      <form onSubmit={submit} className="card w-full max-w-sm space-y-4">
        <div className="text-center">
          <div className="text-4xl">🚪</div>
          <h1 className="mt-2 text-xl font-semibold">Smart Door AI</h1>
          <p className="text-sm text-slate-400">Admin login</p>
        </div>
        <input className="input" placeholder="Username" value={u} onChange={(e) => setU(e.target.value)} autoFocus />
        <input className="input" type="password" placeholder="Password" value={p} onChange={(e) => setP(e.target.value)} />
        {err && <div className="text-sm text-rose-400">{err}</div>}
        <button className="btn-primary w-full" disabled={busy || !u || !p}>{busy ? "Signing in…" : "Sign in"}</button>
      </form>
    </div>
  );
}
