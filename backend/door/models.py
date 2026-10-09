from django.db import models


class Person(models.Model):
    """A person who may be granted door access (not a dashboard login)."""
    ROLES = [("admin", "Admin"), ("resident", "Resident"), ("guest", "Guest")]
    STATUSES = [("active", "Active"), ("disabled", "Disabled")]

    full_name = models.CharField(max_length=120)
    role = models.CharField(max_length=20, choices=ROLES, default="resident")
    status = models.CharField(max_length=20, choices=STATUSES, default="active")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.full_name


class FaceProfile(models.Model):
    person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name="faces")
    embedding = models.JSONField()          # 512-d L2-normalised vector
    quality = models.FloatField(default=0.0)
    image_path = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class AccessLog(models.Model):
    EVENTS = [
        ("GRANTED", "Granted"), ("DENIED", "Denied"), ("UNKNOWN", "Unknown face"),
        ("LIVENESS_FAIL", "Liveness failed"), ("LOCKOUT", "Lockout"),
        ("MANUAL_UNLOCK", "Manual unlock"), ("MANUAL_LOCK", "Manual lock"),
    ]
    person = models.ForeignKey(Person, null=True, blank=True, on_delete=models.SET_NULL, related_name="logs")
    event_type = models.CharField(max_length=20, choices=EVENTS, db_index=True)
    confidence = models.FloatField(null=True, blank=True)
    device = models.CharField(max_length=60, blank=True)
    detail = models.CharField(max_length=255, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-timestamp"]


class IoTDevice(models.Model):
    device_id = models.CharField(max_length=60, unique=True)
    name = models.CharField(max_length=120, blank=True)
    connection_status = models.CharField(max_length=20, default="offline")
    door_state = models.CharField(max_length=20, default="locked")
    last_heartbeat = models.DateTimeField(null=True, blank=True)
    firmware = models.CharField(max_length=40, blank=True)


class SystemSetting(models.Model):
    key = models.CharField(max_length=60, primary_key=True)
    value = models.JSONField()
