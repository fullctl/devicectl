# Generated by Django 3.2.15 on 2023-04-19 16:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('django_devicectl', '0020_alter_deviceoperationalstatus_event'),
    ]

    operations = [
        migrations.AlterField(
            model_name='deviceoperationalstatus',
            name='error_message',
            field=models.TextField(blank=True, help_text='Configuration error', max_length=255, null=True),
        ),
    ]
