# Generated by Django 3.2.19 on 2023-07-11 12:24

import django.db.models.manager
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("django_devicectl", "0025_port_meta"),
    ]

    operations = [
        migrations.CreateModel(
            name="UpdateTrafficGraphs",
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
            name="meta",
            field=models.JSONField(
                blank=True,
                default=dict,
                help_text="Meta data for this device",
                null=True,
            ),
        ),
    ]
