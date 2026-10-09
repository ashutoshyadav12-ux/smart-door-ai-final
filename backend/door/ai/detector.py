"""InsightFace (RetinaFace det + ArcFace rec) loader. Lazy: heavy models load on first use."""
import threading

_app = None
_lock = threading.Lock()


def get_app():
    global _app
    if _app is None:
        with _lock:
            if _app is None:
                from insightface.app import FaceAnalysis  # imported lazily
                app = FaceAnalysis(name="buffalo_l", providers=["CPUExecutionProvider"])
                app.prepare(ctx_id=-1, det_size=(640, 640))
                _app = app
    return _app


def detect(img_bgr):
    """Return insightface Face objects sorted by bbox area (largest first)."""
    faces = get_app().get(img_bgr)
    return sorted(faces, key=lambda f: (f.bbox[2] - f.bbox[0]) * (f.bbox[3] - f.bbox[1]), reverse=True)
