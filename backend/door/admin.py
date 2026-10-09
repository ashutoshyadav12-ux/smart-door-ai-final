from django.contrib import admin
from .models import AccessLog, FaceProfile, IoTDevice, Person, SystemSetting

for m in (Person, FaceProfile, AccessLog, IoTDevice, SystemSetting):
    admin.site.register(m)
