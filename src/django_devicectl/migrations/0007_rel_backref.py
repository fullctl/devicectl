# Generated by Django 3.2.14 on 2022-07-19 13:04

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("django_fullctl", "0019_default_org"),
        ("django_devicectl", "0006_device_facility"),
    ]

    operations = [
        migrations.AlterField(
            model_name="device",
            name="instance",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="devices",
                to="django_fullctl.instance",
            ),
        ),
        migrations.AlterField(
            model_name="facility",
            name="instance",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="facilities",
                to="django_fullctl.instance",
            ),
        ),
        migrations.AlterField(
            model_name="logicalport",
            name="instance",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="logical_ports",
                to="django_fullctl.instance",
            ),
        ),
        migrations.AlterField(
            model_name="physicalport",
            name="device",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="physical_ports",
                to="django_devicectl.device",
            ),
        ),
        migrations.AlterField(
            model_name="virtualport",
            name="logical_port",
            field=models.ForeignKey(
                help_text="logical port",
                on_delete=django.db.models.deletion.CASCADE,
                related_name="virtual_ports",
                to="django_devicectl.logicalport",
            ),
        ),
    ]
