from .base import BaseAPITest, img


class IntegrationTests(BaseAPITest):
    def test_full_flow_dashboard_stats(self):
        uid = self.client.post("/api/users", {"full_name": "Bob"}, format="json").data["id"]
        self.client.post("/api/faces/enroll", {"person_id": uid, "image": img("bob")}, format="multipart")
        self.client.post("/api/faces/recognize", {"image": img("bob")}, format="multipart")
        s = self.client.get("/api/dashboard/stats").data
        self.assertEqual((s["people"], s["enrolled_people"], s["granted_24h"]), (1, 1, 1))
        self.assertEqual(s["door"]["state"], "unlocked")
