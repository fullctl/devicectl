from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from django_devicectl.models.devicectl import IPAddress, Port, PortInfo, VirtualPort
from django_devicectl.models.tasks import RequestPeerctlSync
from fullctl.django.models.concrete.tasks import TaskLimitError


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
