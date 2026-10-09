import threading
import time

from .controller import IoTController


class DemoController(IoTController):
    """Software door: locked <-> unlocked with auto-relock countdown."""
    device_id = "demo-door"

    def __init__(self):
        self._lock = threading.RLock()
        self._state = "locked"
        self._timer = None
        self._until = 0.0

    def unlock(self, duration: int = 5) -> dict:
        with self._lock:
            if self._timer:
                self._timer.cancel()
            self._state = "unlocked"
            self._until = time.time() + duration
            self._timer = threading.Timer(duration, self._relock)
            self._timer.daemon = True
            self._timer.start()
        return self.status()

    def _relock(self):
        with self._lock:
            self._state = "locked"
            self._until = 0.0

    def lock(self) -> dict:
        with self._lock:
            if self._timer:
                self._timer.cancel()
            self._relock()
        return self.status()

    def status(self) -> dict:
        with self._lock:
            remaining = max(0, round(self._until - time.time(), 1)) if self._state == "unlocked" else 0
            return {"mode": "demo", "device_id": self.device_id, "connection": "online",
                    "state": self._state, "seconds_remaining": remaining}
