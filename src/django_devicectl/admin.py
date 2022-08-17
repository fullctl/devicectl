from django.contrib import admin

# from django.utils.translation import gettext as _
from django_handleref.admin import VersionAdmin

from django_devicectl.models import Device, LogicalPort, PhysicalPort, VirtualPort


@admin.register(Device)
class DeviceAdmin(VersionAdmin):
    list_display = ("id", "org", "name", "type", "created", "updated")


@admin.register(LogicalPort)
class LogicalPortAdmin(VersionAdmin):
    list_display = ("id", "org", "name", "trunk", "channel", "created", "updated")


@admin.register(PhysicalPort)
class PhysicalPortAdmin(VersionAdmin):
    list_display = ("id", "org", "device", "name", "logical_port", "created", "updated")


@admin.register(VirtualPort)
class VirtualPortAdmin(VersionAdmin):
    list_display = ("id", "org", "logical_port", "vlan_id", "created", "updated")
