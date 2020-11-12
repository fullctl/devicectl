from django.db import models
from django.utils.translation import gettext_lazy as _

import reversion

from django_inet.models import (
    ASNField,
)

import django_peeringdb.models.concrete as pdb_models

from django_grainy.decorators import grainy_model

from fullctl.django.models.concrete import Instance
from fullctl.django.models.abstract import PdbRefModel, HandleRefModel
from fullctl.django.inet.fields import DeviceDescriptionField
from fullctl.django.inet.const import *


@reversion.register()
@grainy_model(namespace="device", namespace_instance="device.{instance.org.permission_id}.{instance.id}")
class Device(HandleRefModel):
    instance = models.ForeignKey(
        Instance, related_name="device_set", on_delete=models.CASCADE
    )

    name = models.CharField(max_length=255)
    description = DeviceDescriptionField()
    type = models.CharField(
        max_length=255,
        help_text=_("Type of device (software)"),
        choices=DEVICE_TYPES,
    )

    class HandleRef:
        tag = "device"
        unique_together = (("instance", "name"),)

    class Meta:
        db_table = "devicectl_device"
        verbose_name = _("Device")
        verbose_name_plural = _("Devices")

    @property
    def display_name(self):
        return self.name

    @property
    def logport_qs(self):
        logport_ids = [p.logport_id for p in self.phyport_qs.all()]
        return LogicalPort.objects.filter(id__in=logport_ids)

    @property
    def virtport_qs(self):
        return VirtualPort.objects.filter(logport__in=self.logport_qs)

    @property
    def port_qs(self):
        return Port.objects.filter(virtport__in=self.virtport_qs)

    @property
    def org(self):
        return self.instance.org

    def __str__(self):
        return f"{self.name} [#{self.id}]"



@reversion.register()
@grainy_model(namespace="phyport", namespace_instance="phyport.{instance.org.permission_id}.{instance.id}")
class PhysicalPort(HandleRefModel):
    device = models.ForeignKey(
        Device,
        related_name="phyport_set",
        on_delete=models.CASCADE,
    )
    name = models.CharField(max_length=255)
    description = DeviceDescriptionField()

    logport = models.ForeignKey(
        "django_devicectl.LogicalPort",
        help_text=_("Logical port this physical port is a member of"),
        related_name="phyport_qs",
        on_delete=models.CASCADE,
    )

    class HandleRef:
        tag = "phyport"

    class Meta:
        db_table = "devicectl_phyport"
        verbose_name = _("Physical Port")
        verbose_name_plural = _("Physical Ports")

    @property
    def org(self):
        return self.device.instance.org

    def __str__(self):
        return f"{self.name} [{self.org} #{self.id}]"




@reversion.register()
@grainy_model(namespace="logport", namespace_instance="logport.{instance.org.permission_id}.{instance.id}")
class LogicalPort(HandleRefModel):
    """
    Logical port a peering session is build on
    could be a vlan ID on a physical port
    for LAGS, would be the ae port
    """

    instance = models.ForeignKey(
        Instance, related_name="logport_set", on_delete=models.CASCADE
    )
    name = models.CharField(max_length=255, blank=True)
    description = DeviceDescriptionField()
    trunk = models.IntegerField(blank=True, null=True)
    channel = models.IntegerField(blank=True, null=True)

    class HandleRef:
        tag = "logport"

    class Meta:
        db_table = "devctl_logport"
        verbose_name = _("Logical Port")
        verbose_name_plural = _("Logical Ports")


    @property
    def org(self):
        return self.instance.org

    def __str__(self):
        return f"{self.name} [{self.org} #{self.id}]"

@reversion.register()
@grainy_model(namespace="virtport", namespace_instance="virtport.{instance.org.permission_id}.{instance.id}")
class VirtualPort(HandleRefModel):
    """
    Port a peering session is build on, ties a virtual port back to a logical port
    """

    logport = models.ForeignKey(
        LogicalPort,
        help_text="logical port",
        related_name="virtport_set",
        on_delete=models.CASCADE,
    )

    vlan_id = models.IntegerField()

    class HandleRef:
        tag = "virtport"

    class Meta:
        db_table = "devicectl_virtport"
        verbose_name = _("Virtual Port")
        verbose_name_plural = _("Virtual Ports")

    @property
    def org(self):
        return self.logport.instance.org


    def __str__(self):
        return f"#{self.id} [{self.logport}]"




