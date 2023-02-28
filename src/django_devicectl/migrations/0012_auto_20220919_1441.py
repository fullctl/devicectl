# Generated by Django 3.2.15 on 2022-09-19 14:41

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("django_devicectl", "0011_auto_20220909_0913"),
    ]

    operations = [
        migrations.AddField(
            model_name="port",
            name="name",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name="physicalport",
            name="logical_port",
            field=models.ForeignKey(
                help_text="Logical port this physical port is a member of",
                on_delete=django.db.models.deletion.CASCADE,
                related_name="physical_ports",
                to="django_devicectl.logicalport",
            ),
        ),
    ]
