# Generated by Django 3.2.15 on 2023-04-19 10:37

import django.db.models.deletion
import django.db.models.manager
import django_handleref.models
import fullctl.django.fields.service_bridge
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("django_devicectl", "0018_dummy_port_prefix"),
    ]

    operations = [
        migrations.CreateModel(
            name="RequestPeerctlSync",
            fields=[],
            options={
                "proxy": True,
                "indexes": [],
                "constraints": [],
            },
            bases=("django_fullctl.task",),
            managers=[
                ("handleref", django.db.models.manager.Manager()),
            ],
        ),
        migrations.CreateModel(
            name="DeviceOperationalStatus",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                (
                    "created",
                    django_handleref.models.CreatedDateTimeField(
                        auto_now_add=True, verbose_name="Created"
                    ),
                ),
                (
                    "updated",
                    django_handleref.models.UpdatedDateTimeField(
                        auto_now=True, verbose_name="Updated"
                    ),
                ),
                ("version", models.IntegerField(default=0)),
                (
                    "status",
                    models.CharField(
                        choices=[("ok", "ok"), ("error", "Error")],
                        default="ok",
                        help_text="Configuration status",
                        max_length=255,
                    ),
                ),
                (
                    "error_message",
                    models.CharField(
                        blank=True,
                        help_text="Configuration error",
                        max_length=255,
                        null=True,
                    ),
                ),
                (
                    "event",
                    fullctl.django.fields.service_bridge.ReferencedObjectField(
                        blank=True,
                        bridge_type="event",
                        help_text="auditCtl event reference",
                        null=True,
                    ),
                ),
                (
                    "device",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="operational_status",
                        to="django_devicectl.device",
                    ),
                ),
            ],
            options={
                "verbose_name": "Device Operational Status",
                "verbose_name_plural": "Device Operational Statuses",
                "db_table": "devicectl_device_operational_status",
            },
            managers=[
                ("handleref", django.db.models.manager.Manager()),
            ],
        ),
    ]