# Generated by Django 3.2.4 on 2021-06-15 14:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("django_devicectl", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="virtualport",
            name="name",
            field=models.CharField(blank=True, max_length=255),
        ),
    ]
