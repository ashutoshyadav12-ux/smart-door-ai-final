import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from door.models import IoTDevice


class Command(BaseCommand):
    help = "Create the default dashboard admin and a demo IoT device."

    def handle(self, *args, **opts):
        U = get_user_model()
        name = os.environ.get("ADMIN_USERNAME", "admin")
        pw = os.environ.get("ADMIN_PASSWORD", "admin12345")
        if not U.objects.filter(username=name).exists():
            U.objects.create_superuser(name, "", pw)
            self.stdout.write(self.style.SUCCESS(f"admin '{name}' created"))
        IoTDevice.objects.get_or_create(device_id="door01", defaults={"name": "Front door ESP32"})
        self.stdout.write(self.style.SUCCESS("seed complete"))
