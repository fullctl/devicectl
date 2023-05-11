from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from fullctl.django.models.concrete.tasks import TaskLimitError

from django_devicectl.models.devicectl import (
    DeviceOperationalStatus, 
    DeviceConfigHistory,
    IPAddress, 
    Port, 
    PortInfo, 
    VirtualPort
)
from django_devicectl.models.tasks import RequestPeerctlSync


@receiver(pre_save, sender=IPAddress)
def ip_address_assignment(sender, instance, **kwargs):
    """
    When a new ip address is assigned to a port or
    an existing ip address is moved to a different port
    devicectl needs to let peerctl know that it needs to
    sync its devices and ports from devicectl
    """

    if instance.pk is not None:
        # ip address moved from one port to another ?
        old_instance = IPAddress.objects.get(pk=instance.pk)
        if old_instance.port_info_id != instance.port_info_id:
            try:
                RequestPeerctlSync.create_task(org=instance.instance.org)
            except TaskLimitError:
                pass

    elif instance.port_info_id is not None:
        # new ip address
        try:
            RequestPeerctlSync.create_task(org=instance.instance.org)
        except TaskLimitError:
            pass


@receiver(post_save, sender=VirtualPort)
def auto_create_port(sender, instance, created, **kwargs):
    """
    When a new virtual port is created, create a port
    for it if one does not already exist
    """

    if created:
        port, port_created = Port.objects.get_or_create(virtual_port=instance)
        if port_created:
            port_info = PortInfo.objects.create(instance=instance.logical_port.instance)
            port.port_info = port_info
            port.save()


@receiver(post_save, sender=DeviceOperationalStatus)
def device_config_history(sender, instance, **kwargs):
    """
    When a device operational status is saved, create a
    device config history entry
    """

    latest = instance.device.config_history.order_by("-created").first()

    # only create a new history entry if the config has changed
    if not latest or latest.diff != instance.diff:
        DeviceConfigHistory.objects.create(
            device=instance.device,
            status=instance.status,
            error_message=instance.error_message,
            event=instance.event,
            url_current=instance.url_current,
            url_reference=instance.url_reference,
            config_current=instance.config_current,
            config_reference=instance.config_reference,
        )
