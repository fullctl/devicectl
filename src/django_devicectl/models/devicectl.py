import reversion
from django.db import models
from django.utils.translation import gettext_lazy as _
from django_grainy.decorators import grainy_model
from fullctl.django.fields.service_bridge import ReferencedObjectCharField
from fullctl.django.inet.fields import DeviceDescriptionField
from fullctl.django.models.abstract import (
    GeoModel,
    HandleRefModel,
    ServiceBridgeReferenceModel,
)
from fullctl.django.models.concrete import Instance


@reversion.register()
@grainy_model(
    namespace="facility",
    namespace_instance="facility.{instance.org.permission_id}.{instance.id}",
)
class Facility(GeoModel, ServiceBridgeReferenceModel):
    instance = models.ForeignKey(
        Instance, related_name="facilities", on_delete=models.CASCADE
    )

    name = models.CharField(max_length=255)

    reference = ReferencedObjectCharField(
        bridge_type="facility", max_length=255, null=True, blank=True
    )
    slug = models.SlugField(max_length=64, unique=False, blank=False, null=False)

    class HandleRef:
        tag = "facility"
        verbose_name = _("Facility")
        verbose_name_plural = _("Facilities")

    class ServiceBridge:
        map_pdbctl = {
            "name": "name",
            "address1": "address1",
            "address2": "address2",
            "zipcode": "zipcode",
            "city": "city",
            "country": "country",
            "longitude": "longitude",
            "latitude": "latitude",
        }

        map_nautobot = {
            "name": "name",
            "custom_fields.devicectl_id": "fullctl_id",
            "physical_address": "address1",
            "latitude" : "latitude",
            "longitude" : "longitude",
            "status": "nautobot_status",
        }

    class Meta:
        db_table = "devicectl_facility"
        constraints = [
            models.UniqueConstraint(
                fields=["instance", "slug"], name="unique_slug_instance_pair"
            )
        ]

    @property
    def org(self):
        return self.instance.org

    @property
    def nautobot_status(self):
        if self.status == "ok":
            return "active"

    def __str__(self):
        return f"{self.name} [#{self.id}]"


@reversion.register()
@grainy_model(
    namespace="device",
    namespace_instance="device.{instance.org.permission_id}.{instance.id}",
)
class Device(ServiceBridgeReferenceModel):
    instance = models.ForeignKey(
        Instance, related_name="devices", on_delete=models.CASCADE
    )
    facility = models.ForeignKey(
        Facility,
        related_name="devices",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text=_("Device is located in this facility"),
    )

    name = models.CharField(max_length=255)
    description = DeviceDescriptionField()
    type = models.CharField(
        max_length=255,
        help_text=_("Type of device (software)"),
    )

    reference = ReferencedObjectCharField(
        bridge_type="device", max_length=255, null=True, blank=True
    )

    reference = ReferencedObjectCharField(
        bridge_type="device", max_length=255, null=True, blank=True
    )

    class HandleRef:
        tag = "device"
        unique_together = (("instance", "name"),)

    class ServiceBridge:
        map_nautobot = {
            "display": "name",
            "comments": "description",
            "device_type.model": "type",
        }

    class Meta:
        db_table = "devicectl_device"
        verbose_name = _("Device")
        verbose_name_plural = _("Devices")
        indexes = [
            models.Index("reference", name="device_reference"),
        ]

    @property
    def display_name(self):
        return self.name

    @property
    def logical_port_qs(self):
        logical_port_ids = [p.logical_port_id for p in self.physical_port_qs.all()]
        return LogicalPort.objects.filter(id__in=logical_port_ids)

    @property
    def virtual_port_qs(self):
        return VirtualPort.objects.filter(logical_port__in=self.logical_port_qs)

    @property
    def port_qs(self):
        return None
        # TODO Port?
        # return Port.objects.filter(virtual_port__in=self.virtual_port_qs)

    @property
    def org(self):
        return self.instance.org

    def __str__(self):
        return f"{self.name} [#{self.id}]"


@reversion.register()
@grainy_model(
    namespace="physical_port",
    namespace_instance="physical_port.{instance.org.permission_id}.{instance.id}",
)
class PhysicalPort(HandleRefModel):
    device = models.ForeignKey(
        Device,
        related_name="physical_ports",
        on_delete=models.CASCADE,
    )
    name = models.CharField(max_length=255)
    description = DeviceDescriptionField()

    logical_port = models.ForeignKey(
        "django_devicectl.LogicalPort",
        help_text=_("Logical port this physical port is a member of"),
        related_name="physical_port_qs",
        on_delete=models.CASCADE,
    )

    class HandleRef:
        tag = "physical_port"

    class Meta:
        db_table = "devicectl_physical_port"
        verbose_name = _("Physical Port")
        verbose_name_plural = _("Physical Ports")

    @property
    def org(self):
        return self.device.instance.org

    @property
    def display_name(self):
        return self.name

    @property
    def device_name(self):
        return self.device.name

    @property
    def logical_port_name(self):
        return self.logical_port.name

    def __str__(self):
        return f"{self.name} [{self.org} #{self.id}]"


@reversion.register()
@grainy_model(
    namespace="logical_port",
    namespace_instance="logical_port.{instance.org.permission_id}.{instance.id}",
)
class LogicalPort(HandleRefModel):
    """
    Logical port defines how to interact with multiple physical interfaces.

    For example:
        - an access port to a vlan ID on a physical port
        - trunk port
        - a LAG (ae port)
    """

    instance = models.ForeignKey(
        Instance, related_name="logical_ports", on_delete=models.CASCADE
    )
    name = models.CharField(max_length=255, blank=True)
    description = DeviceDescriptionField()
    trunk = models.IntegerField(blank=True, null=True)
    channel = models.IntegerField(blank=True, null=True)

    class HandleRef:
        tag = "logical_port"

    class Meta:
        db_table = "devctl_logical_port"
        verbose_name = _("Logical Port")
        verbose_name_plural = _("Logical Ports")

    @property
    def display_name(self):
        return self.name

    @property
    def org(self):
        return self.instance.org

    def __str__(self):
        return f"{self.name} [{self.org} #{self.id}]"


@reversion.register()
@grainy_model(
    namespace="virtual_port",
    namespace_instance="virtual_port.{instance.org.permission_id}.{instance.id}",
)
class VirtualPort(HandleRefModel):
    """
    Port a peering session is build on, ties a virtual port back to a logical port
    """

    name = models.CharField(max_length=255, blank=True)

    logical_port = models.ForeignKey(
        LogicalPort,
        help_text="logical port",
        related_name="virtual_ports",
        on_delete=models.CASCADE,
    )

    vlan_id = models.IntegerField()

    class HandleRef:
        tag = "virtual_port"

    class Meta:
        db_table = "devicectl_virtual_port"
        verbose_name = _("Virtual Port")
        verbose_name_plural = _("Virtual Ports")

    @property
    def org(self):
        return self.logical_port.instance.org

    @property
    def display_name(self):
        return self.name

    @property
    def logical_port_name(self):
        return self.logical_port.name

    def __str__(self):
        return f"#{self.id} [{self.logical_port}]"
