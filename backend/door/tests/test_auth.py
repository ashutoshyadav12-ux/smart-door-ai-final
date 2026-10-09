from rest_framework.test import APIClient
from .base import BaseAPITest


class AuthTests(BaseAPITest):
    def test_login_ok_and_me(self):
        self.assertEqual(self.client.get("/api/auth/me").data["username"], "admin")

    def test_bad_password(self):
        r = APIClient().post("/api/auth/login", {"username": "admin", "password": "x"}, format="json")
        self.assertEqual(r.status_code, 401)

    def test_protected(self):
        self.assertEqual(APIClient().get("/api/users").status_code, 401)
