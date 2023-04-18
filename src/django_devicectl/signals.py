from django_devicectl.models.devicectl import IPAddress
from django_devicectl.models.tasks import RequestPeerctlSync
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver

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
            RequestPeerctlSync.create_task(org=instance.instance.org)

    elif instance.port_info_id is not None:
        # new ip address
        RequestPeerctlSync.create_task(org=instance.instance.org)
