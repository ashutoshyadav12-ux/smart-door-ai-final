from .base import BaseAPITest


class IoTTests(BaseAPITest):
    def test_manual_unlock_lock(self):
        self.assertEqual(self.client.post("/api/door/unlock", {"duration": 5}, format="json").data["state"], "unlocked")
        self.assertEqual(self.client.post("/api/door/lock").data["state"], "locked")

    def test_command_and_heartbeat(self):
        self.client.post("/api/iot/command", {"action": "unlock"}, format="json")
        self.assertEqual(self.client.get("/api/door/status").data["state"], "unlocked")
        bad = self.client.post("/api/iot/heartbeat", {"device_id": "d1"}, format="json")
        self.assertEqual(bad.status_code, 401)
        ok = self.client.post("/api/iot/heartbeat", {"device_id": "d1"}, format="json", HTTP_X_DEVICE_KEY="esp32-shared-secret")
        self.assertEqual(ok.status_code, 200)
        self.assertEqual(len(self.client.get("/api/iot/devices").data), 1)
