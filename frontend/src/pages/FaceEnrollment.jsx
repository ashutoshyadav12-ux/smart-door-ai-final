import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import api from "../api/client.js";
import useWebcam from "../hooks/useWebcam.js";

const STEPS = ["Look straight at the camera", "Turn slightly left", "Turn slightly right", "Tilt chin up a little", "Neutral face, good lighting"];

export default function FaceEnrollment() {
  const [params] = useSearchParams();
  const [people, setPeople] = useState([]);
  const [pid, setPid] = useState(params.get("person") || "");
  const [saved, setSaved] = useState(0);
  const [msg, setMsg] = useState(null);
  const [busy, setBusy] = useState(false);
  const cam = useWebcam();

  useEffect(() => { api.get("/users").then((r) => setPeople(r.data.results ?? r.data)); }, []);
  useEffect(() => {
    const p = people.find((x) => String(x.id) === String(pid));
    setSaved(p ? p.face_samples : 0);
  }, [pid, people]);

  const capture = async () => {
    setBusy(true); setMsg(null);
    try {
      const blob = await cam.capture();
      if (!blob) return setMsg({ ok: false, text: "No frame yet — start the camera first." });
      const fd = new FormData();
      fd.append("person_id", pid);
      fd.append("image", blob, "sample.jpg");
      try {
        const { data } = await api.post("/faces/enroll", fd);
        setSaved(data.total_samples);
        setMsg({ ok: true, text: "Sample saved ✔" });
      } catch (e) {
        const rej = e.response?.data?.rejected?.[0]?.reason;
        setMsg({ ok: false, text: `Rejected: ${rej || "unknown error"}` });
      }
    } finally { setBusy(false); }
  };

  const step = STEPS[Math.min(saved, STEPS.length - 1)];
  return (
    <div className="space-y-4">
      <h2 className="text-xl font-semibold">Face Enrollment</h2>
      <div className="grid gap-5 lg:grid-cols-2">
        <div className="card space-y-3">
          <video ref={cam.videoRef} className="aspect-video w-full rounded-lg bg-black" muted playsInline />
          {cam.error && <div className="text-sm text-rose-400">{cam.error}</div>}
          <div className="flex gap-2">
            {!cam.ready ? <button className="btn-primary" onClick={cam.start}>Start camera</button> : <button className="btn-ghost" onClick={cam.stop}>Stop camera</button>}
          </div>
        </div>
        <div className="card space-y-4">
          <select className="input" value={pid} onChange={(e) => setPid(e.target.value)}>
            <option value="">Select a person…</option>
            {people.map((p) => <option key={p.id} value={p.id}>{p.full_name}</option>)}
          </select>
          <div>
            <div className="mb-1 flex justify-between text-sm"><span>Samples</span><span>{saved} / {STEPS.length}</span></div>
            <div className="h-2 rounded bg-slate-800"><div className="h-2 rounded bg-indigo-500" style={{ width: `${Math.min(100, (saved / STEPS.length) * 100)}%` }} /></div>
          </div>
          <div className="rounded-lg bg-slate-800 p-3 text-sm">👉 {saved >= STEPS.length ? "Enrollment complete! You can add more samples." : step}</div>
          <button className="btn-primary w-full" disabled={!pid || !cam.ready || busy} onClick={capture}>{busy ? "Processing…" : "Capture sample"}</button>
          {msg && <div className={`text-sm ${msg.ok ? "text-emerald-400" : "text-amber-400"}`}>{msg.text}</div>}
        </div>
      </div>
    </div>
  );
}
