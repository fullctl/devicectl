# Generated by Django 3.2.14 on 2022-07-18 14:52

import django.db.models.manager
import fullctl.django.fields.service_bridge
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("django_fullctl", "0019_default_org"),
        ("django_devicectl", "0002_virtualport_name"),
    ]

    operations = [
        migrations.CreateModel(
            name="NautobotPull",
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
        migrations.AddField(
            model_name="device",
            name="reference",
            field=fullctl.django.fields.service_bridge.ReferencedObjectField(
                blank=True, bridge_type="device", null=True
            ),
        ),
    ]
