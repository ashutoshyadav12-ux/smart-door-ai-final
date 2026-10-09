"""In-memory embedding matrix so recognition is one matrix-vector product."""
import threading

import numpy as np

from .similarity import cosine_matrix, normalize


class VectorCache:
    def __init__(self):
        self._lock = threading.Lock()
        self._loaded = False
        self.ids = np.empty(0, dtype=np.int64)
        self.matrix = np.empty((0, 512), dtype=np.float32)

    def reload(self):
        from ..models import FaceProfile
        rows = list(FaceProfile.objects.filter(person__status="active").values_list("person_id", "embedding"))
        with self._lock:
            if rows:
                self.ids = np.array([r[0] for r in rows], dtype=np.int64)
                self.matrix = np.stack([normalize(r[1]) for r in rows]).astype(np.float32)
            else:
                self.ids = np.empty(0, dtype=np.int64)
                self.matrix = np.empty((0, 512), dtype=np.float32)
            self._loaded = True

    def search(self, embedding):
        """Return (person_id | None, best_cosine_score)."""
        if not self._loaded:
            self.reload()
        with self._lock:
            if len(self.ids) == 0:
                return None, 0.0
            scores = cosine_matrix(self.matrix, embedding)
            i = int(np.argmax(scores))
            return int(self.ids[i]), float(scores[i])


cache = VectorCache()
