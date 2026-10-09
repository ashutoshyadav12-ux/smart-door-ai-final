import { useEffect, useRef, useState } from "react";
import api from "../api/client.js";
import useWebcam from "../hooks/useWebcam.js";

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const REASONS = {
  no_face: "No face detected", too_dark: "Too dark", too_bright: "Too bright", too_blurry: "Too blurry",
  face_too_small: "Move closer", unknown_face: "Unknown face", locked_out: "System locked (too many failures)",
  liveness_failed: "Liveness check failed — blink or move slightly",
};

export default function LiveRecognition() {
  const cam = useWebcam();
  const { capture } = cam;
  const [running, setRunning] = useState(false);
  const [result, setResult] = useState(null);
  const busy = useRef(false);

  useEffect(() => {
    if (!running) return;
    const tick = async () => {
      if (busy.current) return;
      busy.current = true;
      try {
        const { data: cfg } = await api.get("/settings");
        const n = cfg.liveness_required ? 3 : 1;
        const fd = new FormData();
        for (let i = 0; i < n; i++) {
          const b = await capture();
          if (b) fd.append("image", b, `f${i}.jpg`);
          if (i < n - 1) await sleep(300);
        }
        if (![...fd.keys()].length) return;
        const { data } = await api.post("/faces/recognize", fd);
        setResult(data);
      } catch (e) {
        setResult({ granted: false, reason: "error" });
      } finally { busy.current = false; }
    };
    const t = setInterval(tick, 2000);
    return () => clearInterval(t);
  }, [running, capture]);

  const granted = result?.granted;
  return (
    <div className="space-y-4">
      <h2 className="text-xl font-semibold">Live Recognition</h2>
      <div className="grid gap-5 lg:grid-cols-2">
        <div className="card space-y-3">
          <video ref={cam.videoRef} className={`aspect-video w-full rounded-lg bg-black ring-4 ${result ? (granted ? "ring-emerald-500" : "ring-rose-500") : "ring-transparent"}`} muted playsInline />
          {cam.error && <div className="text-sm text-rose-400">{cam.error}</div>}
          <div className="flex gap-2">
            {!cam.ready ? <button className="btn-primary" onClick={cam.start}>Start camera</button> : <button className="btn-ghost" onClick={() => { setRunning(false); cam.stop(); }}>Stop camera</button>}
            <button className="btn-primary" disabled={!cam.ready} onClick={() => setRunning((r) => !r)}>{running ? "Pause scan" : "Start scanning"}</button>
          </div>
        </div>
        <div className="card flex min-h-[220px] flex-col items-center justify-center gap-2 text-center">
          {!result && <div className="text-slate-400">{running ? "Scanning…" : "Start the camera, then scanning."}</div>}
          {result && (
            <>
              <div className="text-5xl">{granted ? "✅" : "⛔"}</div>
              <div className="text-xl font-semibold">{granted ? `Welcome, ${result.person}` : "Access denied"}</div>
              <div className="text-sm text-slate-400">
                {granted ? (result.reason === "cooldown" ? "Already unlocked recently" : "Door unlocked") : REASONS[result.reason] || result.reason}
                {result.retry_after ? ` · retry in ${result.retry_after}s` : ""}
              </div>
              {result.confidence != null && <div className="text-xs text-slate-500">confidence {result.confidence}</div>}
            </>
          )}
        </div>
      </div>
    </div>
  );
}
