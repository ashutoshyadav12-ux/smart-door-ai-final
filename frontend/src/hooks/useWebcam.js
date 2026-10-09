import { useCallback, useEffect, useRef, useState } from "react";

export default function useWebcam() {
  const videoRef = useRef(null);
  const streamRef = useRef(null);
  const [ready, setReady] = useState(false);
  const [error, setError] = useState(null);

  const start = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: { width: 640, height: 480 }, audio: false });
      streamRef.current = stream;
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        await videoRef.current.play();
      }
      setReady(true);
      setError(null);
    } catch (e) {
      setError("Camera access failed. Allow permission (HTTPS or localhost required).");
    }
  }, []);

  const stop = useCallback(() => {
    streamRef.current?.getTracks().forEach((t) => t.stop());
    streamRef.current = null;
    setReady(false);
  }, []);

  useEffect(() => stop, [stop]);

  const capture = useCallback(
    () =>
      new Promise((resolve) => {
        const v = videoRef.current;
        if (!v || !v.videoWidth) return resolve(null);
        const c = document.createElement("canvas");
        c.width = v.videoWidth;
        c.height = v.videoHeight;
        c.getContext("2d").drawImage(v, 0, 0);
        c.toBlob((b) => resolve(b), "image/jpeg", 0.9);
      }),
    []
  );

  return { videoRef, ready, error, start, stop, capture };
}
