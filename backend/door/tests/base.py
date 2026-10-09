from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from rest_framework.test import APITestCase

from door.ai.cache import cache
from door.iot import reset_controller
from door.services import access_control


def img(tag: str, name="f.jpg"):
    return SimpleUploadedFile(name, tag.encode() * 10, content_type="image/jpeg")


@override_settings(AI_BACKEND="mock", IOT_MODE="demo")
class BaseAPITest(APITestCase):
    def setUp(self):
        get_user_model().objects.create_superuser("admin", "", "pw12345")
        r = self.client.post("/api/auth/login", {"username": "admin", "password": "pw12345"}, format="json")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {r.data['access']}")
        access_control.reset()
        reset_controller()
        cache.reload()
