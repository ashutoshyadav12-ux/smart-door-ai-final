import json
import threading
from datetime import datetime, timezone

from django.conf import settings

from .controller import IoTController

CMD_TOPIC = "smartdoor/{device}/cmd"
STATUS_TOPIC = "smartdoor/+/status"
HEARTBEAT_TOPIC = "smartdoor/+/heartbeat"


class MQTTController(IoTController):
    """Publishes commands to the ESP32 and tracks its status/heartbeat topics."""

    def __init__(self):
        import paho.mqtt.client as mqtt
        self.device_id = settings.MQTT_DEVICE_ID
        self._state = {"state": "unknown", "connection": "offline"}
        self._lock = threading.Lock()
        try:
            self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)   # paho >= 2
        except AttributeError:
            self.client = mqtt.Client()                                   # paho 1.x
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        self.client.reconnect_delay_set(min_delay=1, max_delay=30)
        self.client.connect_async(settings.MQTT_HOST, settings.MQTT_PORT, keepalive=30)
        self.client.loop_start()

    def _on_connect(self, client, userdata, *args):
        client.subscribe([(STATUS_TOPIC, 1), (HEARTBEAT_TOPIC, 0)])

    def _on_message(self, client, userdata, msg):
        try:
            payload = json.loads(msg.payload.decode() or "{}")
            device_id = msg.topic.split("/")[1]
            with self._lock:
                if "state" in payload:
                    self._state["state"] = payload["state"]
                self._state["connection"] = "online"
            from ..models import IoTDevice
            IoTDevice.objects.update_or_create(device_id=device_id, defaults={
                "connection_status": "online",
                "door_state": payload.get("state", self._state["state"]),
                "last_heartbeat": datetime.now(timezone.utc),
                "firmware": payload.get("fw", ""),
            })
        except Exception:
            pass

    def _publish(self, payload: dict):
        info = self.client.publish(CMD_TOPIC.format(device=self.device_id), json.dumps(payload), qos=1)
        return {"published": info.rc == 0, **self.status()}

    def unlock(self, duration: int = 5) -> dict:
        return self._publish({"action": "unlock", "duration": duration})

    def lock(self) -> dict:
        return self._publish({"action": "lock"})

    def status(self) -> dict:
        with self._lock:
            return {"mode": "real", "device_id": self.device_id, **self._state}
