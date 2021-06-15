# Generated by Django 3.2.4 on 2021-06-15 10:13

from django.db import migrations, models
import django.db.models.deletion
import django.db.models.manager
import django_handleref.models
import fullctl.django.inet.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('django_fullctl', '0007_auditlog_ip_address'),
    ]

    operations = [
        migrations.CreateModel(
            name='Device',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('created', django_handleref.models.CreatedDateTimeField(auto_now_add=True, verbose_name='Created')),
                ('updated', django_handleref.models.UpdatedDateTimeField(auto_now=True, verbose_name='Updated')),
                ('version', models.IntegerField(default=0)),
                ('status', models.CharField(choices=[('ok', 'Ok'), ('pending', 'Pending'), ('deactivated', 'Deactivated'), ('failed', 'Failed'), ('expired', 'Expired')], default='ok', max_length=12)),
                ('name', models.CharField(max_length=255)),
                ('description', fullctl.django.inet.fields.DeviceDescriptionField(blank=True, max_length=255, null=True)),
                ('type', models.CharField(choices=[('arista', 'Arista EOS'), ('bird', 'BIRD'), ('bird2', 'BIRD 2'), ('cisco', 'Cisco IOS'), ('cisco-xr', 'Ciscoi IOS XR'), ('junos', 'Juniper Junos OS'), ('junos-set', 'Juniper Junos OS set'), ('sros-md', 'Nokia SR OS MD-CLI'), ('sros-classic', 'Nokia SR OS Classic CLI')], help_text='Type of device (software)', max_length=255)),
                ('instance', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='device_set', to='django_fullctl.instance')),
            ],
            options={
                'verbose_name': 'Device',
                'verbose_name_plural': 'Devices',
                'db_table': 'devicectl_device',
            },
            managers=[
                ('handleref', django.db.models.manager.Manager()),
            ],
        ),
        migrations.CreateModel(
            name='LogicalPort',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('created', django_handleref.models.CreatedDateTimeField(auto_now_add=True, verbose_name='Created')),
                ('updated', django_handleref.models.UpdatedDateTimeField(auto_now=True, verbose_name='Updated')),
                ('version', models.IntegerField(default=0)),
                ('status', models.CharField(choices=[('ok', 'Ok'), ('pending', 'Pending'), ('deactivated', 'Deactivated'), ('failed', 'Failed'), ('expired', 'Expired')], default='ok', max_length=12)),
                ('name', models.CharField(blank=True, max_length=255)),
                ('description', fullctl.django.inet.fields.DeviceDescriptionField(blank=True, max_length=255, null=True)),
                ('trunk', models.IntegerField(blank=True, null=True)),
                ('channel', models.IntegerField(blank=True, null=True)),
                ('instance', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='logical_port_set', to='django_fullctl.instance')),
            ],
            options={
                'verbose_name': 'Logical Port',
                'verbose_name_plural': 'Logical Ports',
                'db_table': 'devctl_logical_port',
            },
            managers=[
                ('handleref', django.db.models.manager.Manager()),
            ],
        ),
        migrations.CreateModel(
            name='VirtualPort',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('created', django_handleref.models.CreatedDateTimeField(auto_now_add=True, verbose_name='Created')),
                ('updated', django_handleref.models.UpdatedDateTimeField(auto_now=True, verbose_name='Updated')),
                ('version', models.IntegerField(default=0)),
                ('status', models.CharField(choices=[('ok', 'Ok'), ('pending', 'Pending'), ('deactivated', 'Deactivated'), ('failed', 'Failed'), ('expired', 'Expired')], default='ok', max_length=12)),
                ('vlan_id', models.IntegerField()),
                ('logical_port', models.ForeignKey(help_text='logical port', on_delete=django.db.models.deletion.CASCADE, related_name='virtual_port_set', to='django_devicectl.logicalport')),
            ],
            options={
                'verbose_name': 'Virtual Port',
                'verbose_name_plural': 'Virtual Ports',
                'db_table': 'devicectl_virtual_port',
            },
            managers=[
                ('handleref', django.db.models.manager.Manager()),
            ],
        ),
        migrations.CreateModel(
            name='PhysicalPort',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('created', django_handleref.models.CreatedDateTimeField(auto_now_add=True, verbose_name='Created')),
                ('updated', django_handleref.models.UpdatedDateTimeField(auto_now=True, verbose_name='Updated')),
                ('version', models.IntegerField(default=0)),
                ('status', models.CharField(choices=[('ok', 'Ok'), ('pending', 'Pending'), ('deactivated', 'Deactivated'), ('failed', 'Failed'), ('expired', 'Expired')], default='ok', max_length=12)),
                ('name', models.CharField(max_length=255)),
                ('description', fullctl.django.inet.fields.DeviceDescriptionField(blank=True, max_length=255, null=True)),
                ('device', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='physical_port_set', to='django_devicectl.device')),
                ('logical_port', models.ForeignKey(help_text='Logical port this physical port is a member of', on_delete=django.db.models.deletion.CASCADE, related_name='physical_port_qs', to='django_devicectl.logicalport')),
            ],
            options={
                'verbose_name': 'Physical Port',
                'verbose_name_plural': 'Physical Ports',
                'db_table': 'devicectl_physical_port',
            },
            managers=[
                ('handleref', django.db.models.manager.Manager()),
            ],
        ),
    ]
