from django.contrib import admin

# from django.utils.translation import gettext as _
from django_handleref.admin import VersionAdmin

from django_devicectl.models import (
    Device,
    LogicalPort,
    PhysicalPort,
    Port,
    PortInfo,
    VirtualPort,
)


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
    list_display = ("id", "org", "display_name", "logical_port", "vlan_id", "created", "updated")


@admin.register(Port)
class PortAdmin(VersionAdmin):
    list_display = (
        "id",
        "name",
        "org",
        "virtual_port",
        "port_info",
        "created",
        "updated",
    )


@admin.register(PortInfo)
class PortInfoAdmin(VersionAdmin):
    list_display = (
        "id",
        "org",
        "port",
        "ip_address_4",
        "ip_address_6",
        "is_management",
        "is_routeserver_peer",
        "speed",
        "created",
        "updated",
    )
