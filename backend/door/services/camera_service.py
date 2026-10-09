"""Optional server-side OpenCV capture + MJPEG. (The dashboard can also capture from the
browser webcam and POST frames to /api/faces/recognize.)"""
import threading
import time

from django.conf import settings


class CameraService:
    def __init__(self):
        self._cap = None
        self._frame = None
        self._running = False
        self._fps = 0.0
        self._lock = threading.Lock()

    def start(self) -> bool:
        if self._running:
            return True
        try:
            import cv2
        except ImportError:
            return False
        src = settings.CAMERA_SOURCE
        src = int(src) if str(src).isdigit() else src
        cap = cv2.VideoCapture(src)
        if not cap.isOpened():
            return False
        self._cap, self._running = cap, True
        threading.Thread(target=self._loop, daemon=True).start()
        return True

    def _loop(self):
        last = time.time()
        while self._running:
            ok, frame = self._cap.read()
            if not ok:
                time.sleep(0.05)
                continue
            now = time.time()
            self._fps = 0.9 * self._fps + 0.1 * (1.0 / max(now - last, 1e-3))
            last = now
            with self._lock:
                self._frame = frame

    def stop(self):
        self._running = False
        if self._cap:
            self._cap.release()
            self._cap = None

    def jpeg(self):
        import cv2
        with self._lock:
            frame = self._frame
        if frame is None:
            return None
        ok, buf = cv2.imencode(".jpg", frame)
        return buf.tobytes() if ok else None

    def mjpeg(self):
        while self._running:
            data = self.jpeg()
            if data:
                yield b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + data + b"\r\n"
            time.sleep(0.04)

    def status(self) -> dict:
        return {"running": self._running, "fps": round(self._fps, 1), "source": str(settings.CAMERA_SOURCE)}


camera = CameraService()
