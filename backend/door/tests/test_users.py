from .base import BaseAPITest


class UserTests(BaseAPITest):
    def test_crud(self):
        r = self.client.post("/api/users", {"full_name": "Asha", "role": "resident"}, format="json")
        self.assertEqual(r.status_code, 201)
        uid = r.data["id"]
        self.assertEqual(self.client.patch(f"/api/users/{uid}", {"status": "disabled"}, format="json").data["status"], "disabled")
        self.assertEqual(self.client.get("/api/users").data["count"], 1)
        self.assertEqual(self.client.delete(f"/api/users/{uid}").status_code, 204)
