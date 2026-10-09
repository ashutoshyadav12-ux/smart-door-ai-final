import uuid
from datetime import timedelta

from django.conf import settings
from django.http import HttpResponse, StreamingHttpResponse
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import AccessToken

from .ai.cache import cache
from .ai.pipeline import pipeline
from .iot import get_controller
from .models import AccessLog, FaceProfile, IoTDevice, Person
from .serializers import (AccessLogSerializer, CommandSerializer, EnrollSerializer,
                          IoTDeviceSerializer, PersonSerializer, UnlockSerializer)
from .services import access_control, settings_service
from .services.camera_service import camera
from .services.log_service import log_event, query_logs
from .services.user_service import delete_person

MAX_SAMPLES = 10


# ---------- health / me ----------
@api_view(["GET"])
@permission_classes([AllowAny])
def health(request):
    return Response({"status": "ok", "ai_backend": settings.AI_BACKEND, "iot_mode": settings.IOT_MODE})


@api_view(["GET"])
def me(request):
    u = request.user
    return Response({"id": u.id, "username": u.username, "is_admin": u.is_staff})


# ---------- users ----------
class PersonViewSet(viewsets.ModelViewSet):
    queryset = Person.objects.all().order_by("-created_at")
    serializer_class = PersonSerializer

    def perform_update(self, serializer):
        serializer.save()
        cache.reload()                       # status may have changed (active/disabled)

    def perform_destroy(self, instance):
        delete_person(instance)


# ---------- faces ----------
class EnrollView(APIView):
    """POST multipart: person_id + one or more `image` files. Rejects low-quality samples."""

    def post(self, request):
        s = EnrollSerializer(data={"person_id": request.data.get("person_id"),
                                   "image": request.FILES.getlist("image")})
        s.is_valid(raise_exception=True)
        try:
            person = Person.objects.get(pk=s.validated_data["person_id"])
        except Person.DoesNotExist:
            return Response({"detail": "person not found"}, status=404)

        saved, rejected = 0, []
        for f in s.validated_data["image"]:
            if person.faces.count() >= MAX_SAMPLES:
                rejected.append({"file": f.name, "reason": "max_samples_reached"})
                continue
            data = f.read()
            r = pipeline.analyze(data)
            if not r.face_found or not r.quality_ok:
                rejected.append({"file": f.name, "reason": r.reason or "no_face", "quality": r.quality})
                continue
            path = ""
            if r.crop is not None:
                try:
                    import cv2
                    settings.FACES_DIR.mkdir(parents=True, exist_ok=True)
                    path = str(settings.FACES_DIR / f"{person.id}_{uuid.uuid4().hex[:8]}.jpg")
                    cv2.imwrite(path, r.crop)
                except Exception:
                    path = ""
            FaceProfile.objects.create(person=person, embedding=r.embedding.tolist(),
                                       quality=r.quality, image_path=path)
            saved += 1
        cache.reload()
        code = status.HTTP_201_CREATED if saved else status.HTTP_422_UNPROCESSABLE_ENTITY
        return Response({"saved": saved, "rejected": rejected, "total_samples": person.faces.count()}, status=code)


class RecognizeView(APIView):
    """POST multipart: `image` (1 frame; send 3+ frames if liveness is enabled)."""

    def post(self, request):
        images = [f.read() for f in request.FILES.getlist("image")]
        if not images:
            return Response({"detail": "image required"}, status=400)
        result = access_control.decide(images, device=request.data.get("device", "camera"))
        return Response(result)


@api_view(["DELETE"])
def clear_faces(request, person_id):
    FaceProfile.objects.filter(person_id=person_id).delete()
    cache.reload()
    return Response(status=204)


# ---------- door ----------
@api_view(["GET"])
def door_status(request):
    return Response(get_controller().status())


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def door_unlock(request):
    s = UnlockSerializer(data=request.data)
    s.is_valid(raise_exception=True)
    duration = s.validated_data.get("duration", settings_service.get("unlock_duration"))
    result = get_controller().unlock(duration)
    log_event("MANUAL_UNLOCK", device="dashboard", detail=f"by {request.user.username}")
    return Response(result)


@api_view(["POST"])
def door_lock(request):
    result = get_controller().lock()
    log_event("MANUAL_LOCK", device="dashboard", detail=f"by {request.user.username}")
    return Response(result)


# ---------- camera ----------
@api_view(["GET"])
def camera_status(request):
    return Response(camera.status())


@api_view(["GET"])
@authentication_classes([])
@permission_classes([AllowAny])
def camera_stream(request):
    """<img src="/api/camera/stream?token=JWT"> — img tags can't send headers, so token via query."""
    try:
        AccessToken(request.query_params.get("token", ""))
    except Exception:
        return HttpResponse(status=401)
    if not camera.start():
        return HttpResponse("camera unavailable", status=503)
    return StreamingHttpResponse(camera.mjpeg(), content_type="multipart/x-mixed-replace; boundary=frame")


# ---------- logs ----------
class AccessLogList(ListAPIView):
    serializer_class = AccessLogSerializer

    def get_queryset(self):
        return query_logs(self.request.query_params)


# ---------- IoT ----------
class IoTDeviceList(ListAPIView):
    queryset = IoTDevice.objects.all()
    serializer_class = IoTDeviceSerializer
    pagination_class = None


@api_view(["POST"])
def iot_command(request):
    s = CommandSerializer(data=request.data)
    s.is_valid(raise_exception=True)
    ctl = get_controller()
    if s.validated_data["action"] == "unlock":
        d = s.validated_data.get("duration", settings_service.get("unlock_duration"))
        result = ctl.unlock(d)
        log_event("MANUAL_UNLOCK", device=ctl.device_id, detail=f"iot command by {request.user.username}")
    else:
        result = ctl.lock()
        log_event("MANUAL_LOCK", device=ctl.device_id, detail=f"iot command by {request.user.username}")
    return Response(result)


@api_view(["POST"])
@authentication_classes([])
@permission_classes([AllowAny])
def iot_heartbeat(request):
    """HTTP heartbeat fallback for devices (header X-Device-Key)."""
    if request.headers.get("X-Device-Key") != settings.DEVICE_API_KEY:
        return Response({"detail": "invalid device key"}, status=401)
    device_id = request.data.get("device_id")
    if not device_id:
        return Response({"detail": "device_id required"}, status=400)
    IoTDevice.objects.update_or_create(device_id=device_id, defaults={
        "connection_status": "online", "door_state": request.data.get("state", "locked"),
        "last_heartbeat": timezone.now(), "firmware": request.data.get("fw", "")})
    return Response({"ok": True})


# ---------- settings ----------
class SettingsView(APIView):
    def get(self, request):
        return Response(settings_service.get_all())

    def put(self, request):
        try:
            return Response(settings_service.update(request.data))
        except (ValueError, TypeError) as e:
            return Response({"detail": str(e)}, status=400)


# ---------- dashboard ----------
@api_view(["GET"])
def dashboard_stats(request):
    today = timezone.now() - timedelta(hours=24)
    recent = AccessLog.objects.filter(timestamp__gte=today)
    # mark devices offline if no heartbeat in 30s
    IoTDevice.objects.filter(last_heartbeat__lt=timezone.now() - timedelta(seconds=30)).update(connection_status="offline")
    return Response({
        "people": Person.objects.count(),
        "enrolled_people": Person.objects.filter(faces__isnull=False).distinct().count(),
        "granted_24h": recent.filter(event_type="GRANTED").count(),
        "denied_24h": recent.filter(event_type__in=["UNKNOWN", "DENIED", "LIVENESS_FAIL", "LOCKOUT"]).count(),
        "devices_online": IoTDevice.objects.filter(connection_status="online").count(),
        "door": get_controller().status(),
        "recent": AccessLogSerializer(AccessLog.objects.select_related("person")[:8], many=True).data,
    })
