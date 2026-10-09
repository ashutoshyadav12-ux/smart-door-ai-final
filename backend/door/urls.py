from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from . import views

router = DefaultRouter(trailing_slash=False)
router.register("users", views.PersonViewSet, basename="users")

urlpatterns = [
    path("health", views.health),
    path("auth/login", TokenObtainPairView.as_view()),
    path("auth/refresh", TokenRefreshView.as_view()),
    path("auth/me", views.me),
    path("", include(router.urls)),
    path("faces/enroll", views.EnrollView.as_view()),
    path("faces/recognize", views.RecognizeView.as_view()),
    path("faces/<int:person_id>", views.clear_faces),
    path("door/status", views.door_status),
    path("door/unlock", views.door_unlock),
    path("door/lock", views.door_lock),
    path("camera/status", views.camera_status),
    path("camera/stream", views.camera_stream),
    path("access-logs", views.AccessLogList.as_view()),
    path("iot/devices", views.IoTDeviceList.as_view()),
    path("iot/command", views.iot_command),
    path("iot/heartbeat", views.iot_heartbeat),
    path("settings", views.SettingsView.as_view()),
    path("dashboard/stats", views.dashboard_stats),
]
