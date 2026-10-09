"""Central access decision: recognise -> liveness -> threshold -> cooldown/lockout -> unlock."""
import threading
import time

from ..ai.cache import cache
from ..ai.pipeline import pipeline
from ..iot import get_controller
from ..models import Person
from . import settings_service as cfg
from .log_service import log_event

_lock = threading.Lock()
_state = {"failures": [], "locked_until": 0.0, "last_grant": {}}


def reset():
    with _lock:
        _state.update(failures=[], locked_until=0.0, last_grant={})


def _register_failure(device):
    now = time.time()
    window = cfg.get("lockout_seconds")
    with _lock:
        _state["failures"] = [t for t in _state["failures"] if now - t < window] + [now]
        if len(_state["failures"]) >= cfg.get("max_failed_attempts"):
            _state["locked_until"] = now + window
            _state["failures"] = []
            log_event("LOCKOUT", device=device, detail=f"locked for {window}s after repeated failures")


def decide(images, device="camera") -> dict:
    """images: list[bytes]. First is the recognition frame; extra frames feed liveness."""
    now = time.time()
    with _lock:
        if _state["locked_until"] > now:
            return {"granted": False, "reason": "locked_out",
                    "retry_after": int(_state["locked_until"] - now)}

    results = [pipeline.analyze(b) for b in images]
    first = results[0]
    if not first.face_found:
        return {"granted": False, "reason": first.reason or "no_face"}
    if not first.quality_ok:
        return {"granted": False, "reason": first.reason or "low_quality", "quality": first.quality}

    if cfg.get("liveness_required"):
        ok, why = pipeline.liveness(results)
        if not ok:
            _register_failure(device)
            log_event("LIVENESS_FAIL", device=device, detail=why)
            return {"granted": False, "reason": "liveness_failed", "detail": why}

    person_id, score = cache.search(first.embedding)
    if person_id is None or score < cfg.get("match_threshold"):
        _register_failure(device)
        log_event("UNKNOWN", confidence=score, device=device, detail="no matching profile")
        return {"granted": False, "reason": "unknown_face", "confidence": round(score, 3)}

    person = Person.objects.get(pk=person_id)
    with _lock:
        last = _state["last_grant"].get(person_id, 0)
        in_cooldown = now - last < cfg.get("cooldown_seconds")
    if in_cooldown:
        return {"granted": True, "reason": "cooldown", "person": person.full_name,
                "confidence": round(score, 3)}

    door = get_controller().unlock(cfg.get("unlock_duration"))
    with _lock:
        _state["last_grant"][person_id] = now
        _state["failures"] = []
    log_event("GRANTED", person=person, confidence=score, device=device)
    return {"granted": True, "reason": "match", "person": person.full_name,
            "person_id": person.id, "confidence": round(score, 3), "door": door}
