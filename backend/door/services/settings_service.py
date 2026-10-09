from ..models import SystemSetting

DEFAULTS = {
    "match_threshold": 0.45,     # cosine similarity needed to accept a match
    "unlock_duration": 5,        # seconds
    "liveness_required": False,
    "max_failed_attempts": 5,
    "lockout_seconds": 60,
    "cooldown_seconds": 3,
}


def get(key):
    row = SystemSetting.objects.filter(key=key).first()
    return row.value if row else DEFAULTS[key]


def get_all() -> dict:
    stored = {s.key: s.value for s in SystemSetting.objects.all()}
    return {k: stored.get(k, v) for k, v in DEFAULTS.items()}


def update(data: dict) -> dict:
    for k, v in data.items():
        if k not in DEFAULTS:
            raise ValueError(f"unknown setting: {k}")
        want = type(DEFAULTS[k])
        if want is float:
            v = float(v)
        elif want is int:
            v = int(v)
        elif want is bool:
            v = bool(v)
        SystemSetting.objects.update_or_create(key=k, defaults={"value": v})
    return get_all()
