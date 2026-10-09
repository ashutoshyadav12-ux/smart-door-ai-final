import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Person",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("full_name", models.CharField(max_length=120)),
                ("role", models.CharField(choices=[("admin", "Admin"), ("resident", "Resident"), ("guest", "Guest")], default="resident", max_length=20)),
                ("status", models.CharField(choices=[("active", "Active"), ("disabled", "Disabled")], default="active", max_length=20)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name="FaceProfile",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("embedding", models.JSONField()),
                ("quality", models.FloatField(default=0.0)),
                ("image_path", models.CharField(blank=True, max_length=255)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("person", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="faces", to="door.person")),
            ],
        ),
        migrations.CreateModel(
            name="AccessLog",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("event_type", models.CharField(choices=[("GRANTED", "Granted"), ("DENIED", "Denied"), ("UNKNOWN", "Unknown face"), ("LIVENESS_FAIL", "Liveness failed"), ("LOCKOUT", "Lockout"), ("MANUAL_UNLOCK", "Manual unlock"), ("MANUAL_LOCK", "Manual lock")], db_index=True, max_length=20)),
                ("confidence", models.FloatField(blank=True, null=True)),
                ("device", models.CharField(blank=True, max_length=60)),
                ("detail", models.CharField(blank=True, max_length=255)),
                ("timestamp", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("person", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="logs", to="door.person")),
            ],
            options={"ordering": ["-timestamp"]},
        ),
        migrations.CreateModel(
            name="IoTDevice",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("device_id", models.CharField(max_length=60, unique=True)),
                ("name", models.CharField(blank=True, max_length=120)),
                ("connection_status", models.CharField(default="offline", max_length=20)),
                ("door_state", models.CharField(default="locked", max_length=20)),
                ("last_heartbeat", models.DateTimeField(blank=True, null=True)),
                ("firmware", models.CharField(blank=True, max_length=40)),
            ],
        ),
        migrations.CreateModel(
            name="SystemSetting",
            fields=[
                ("key", models.CharField(max_length=60, primary_key=True, serialize=False)),
                ("value", models.JSONField()),
            ],
        ),
    ]
