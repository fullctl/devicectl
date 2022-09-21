# Generated by Django 3.2.15 on 2022-09-21 14:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('django_devicectl', '0013_alter_port_port_info'),
    ]

    operations = [
        migrations.AlterField(
            model_name='port',
            name='virtual_port',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='port', to='django_devicectl.virtualport'),
        ),
    ]
