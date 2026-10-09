from rest_framework import serializers

from .models import AccessLog, IoTDevice, Person


class PersonSerializer(serializers.ModelSerializer):
    face_samples = serializers.IntegerField(source="faces.count", read_only=True)

    class Meta:
        model = Person
        fields = ["id", "full_name", "role", "status", "created_at", "face_samples"]
        read_only_fields = ["id", "created_at"]


class AccessLogSerializer(serializers.ModelSerializer):
    person_name = serializers.CharField(source="person.full_name", read_only=True, default=None)

    class Meta:
        model = AccessLog
        fields = ["id", "person", "person_name", "event_type", "confidence", "device", "detail", "timestamp"]


class IoTDeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = IoTDevice
        fields = "__all__"


class EnrollSerializer(serializers.Serializer):
    person_id = serializers.IntegerField()
    image = serializers.ListField(child=serializers.FileField(), allow_empty=False, required=False)


class UnlockSerializer(serializers.Serializer):
    duration = serializers.IntegerField(required=False, min_value=1, max_value=60)


class CommandSerializer(serializers.Serializer):
    action = serializers.ChoiceField(choices=["unlock", "lock"])
    duration = serializers.IntegerField(required=False, min_value=1, max_value=60)
