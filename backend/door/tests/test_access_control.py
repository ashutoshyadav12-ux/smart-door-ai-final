from .base import BaseAPITest, img


class AccessTests(BaseAPITest):
    def _enroll(self, tag="alice"):
        uid = self.client.post("/api/users", {"full_name": "Alice"}, format="json").data["id"]
        r = self.client.post("/api/faces/enroll", {"person_id": uid, "image": img(tag)}, format="multipart")
        self.assertEqual(r.status_code, 201)
        return uid

    def test_enrolled_face_unlocks(self):
        self._enroll()
        r = self.client.post("/api/faces/recognize", {"image": img("alice")}, format="multipart")
        self.assertTrue(r.data["granted"])
        self.assertEqual(self.client.get("/api/door/status").data["state"], "unlocked")
        logs = self.client.get("/api/access-logs?event_type=granted").data
        self.assertEqual(logs["count"], 1)

    def test_unknown_face_denied(self):
        self._enroll()
        r = self.client.post("/api/faces/recognize", {"image": img("mallory")}, format="multipart")
        self.assertFalse(r.data["granted"])
        self.assertEqual(r.data["reason"], "unknown_face")

    def test_disabled_user_denied(self):
        uid = self._enroll()
        self.client.patch(f"/api/users/{uid}", {"status": "disabled"}, format="json")
        r = self.client.post("/api/faces/recognize", {"image": img("alice")}, format="multipart")
        self.assertFalse(r.data["granted"])

    def test_lockout_after_failures(self):
        self._enroll()
        self.client.put("/api/settings", {"max_failed_attempts": 3}, format="json")
        for i in range(3):
            self.client.post("/api/faces/recognize", {"image": img(f"bad{i}")}, format="multipart")
        r = self.client.post("/api/faces/recognize", {"image": img("alice")}, format="multipart")
        self.assertEqual(r.data["reason"], "locked_out")

    def test_settings_roundtrip(self):
        r = self.client.put("/api/settings", {"match_threshold": 0.6}, format="json")
        self.assertEqual(r.data["match_threshold"], 0.6)
        self.assertEqual(self.client.put("/api/settings", {"nope": 1}, format="json").status_code, 400)
