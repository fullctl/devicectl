from django.utils.translation import gettext_lazy as _
import fullctl.service_bridge.nautobot as nautobot
from fullctl.django.models.concrete.service_bridge import service_bridge_action

import django_devicectl.models.devicectl as models

@service_bridge_action("nautobot_push_device_loc", _("Nautobot: update device location"))
def push_device_loc(action, device):

    """
    Push handler that pushes a device location (facility/site) change to nautobot
    """

    # this action only works on push
    if action != "push":
        return

    # device main reference source is not nautobot
    # TODO: support as secondary source?
    if device.reference_source != "nautobot":
        return

    # device no longer assigned to a facility
    if not device.facility_id:
        nautobot.Device().partial_update(device.reference.object, {"site": None})
        return
    facility = device.facility

    # site exists in nautobot?
    site = nautobot.Site().first(cf_devicectl_id=facility.id)

    if site:

        # assign device to site in nautobot
        nautobot.Device().partial_update(device.reference.object, {"site": str(site.id)})




def sync_custom_fields():

    """
    Make sure the necessary custom fields exist in nautobot
    """

    nautobot.CustomField().sync(
        [
            {
                # nautobot 1.3.6
                "name": "devicectl_id",
                # nautobot 1.4.1
                "slug": "devicectl_id",
                "label": "deviceCtl ID",
                "content_types": ["dcim.site"],
                "type": "integer",
                "description": "deviceCtl reference id",
                "required": False,
            },
        ]
    )

def pull(org, *args, **kwargs):

    """
    Pull data from nautobot
    """

    instance = models.Instance.objects.get(org=org)

    # FIXME allow per organization set up of nautobot url / token
    # currently uses globally configured values for both

    references = []

    # create / update devices from nautobot data

    for nautobot_device in nautobot.Device().objects():
        device, created = models.Device.objects.get_or_create(
            reference=nautobot_device.id, instance=instance
        )
        references.append(device.reference)
        changed = device.sync_from_reference(ref_obj=nautobot_device)

        if changed or created:
            device.save()

    # delete devices that no longer exist in nautobot

    qset_remove = models.Device.objects.exclude(reference__in=references).exclude(
        reference__isnull=True
    )

    qset_remove.delete()



def push(org, *args, **kwargs):

    """
    Push data to nautobot
    """

    # make sure required custom fields exist on the nautobot side

    sync_custom_fields()

    # preload nautobot data

    nautobot_sites = [fac for fac in nautobot.Site().objects()]
    nautobot_devices = [dev for dev in nautobot.Device().objects()]

    # sync devicectl facility -> nautobot site

    for fac in models.Facility.objects.all():

        exists = False

        for nautobot_site in nautobot_sites:

            if nautobot_site.custom_fields.devicectl_id == fac.id:
                exists = nautobot_site
                break

        if not exists:
            nautobot_site = nautobot.Site().create(fac.service_bridge_data("nautobot"))
            #nautobot_site = nautobot.Site().object(data["id"])
        else:
            nautobot.Site().update(exists, fac.service_bridge_data("nautobot"))

        # assign nautobot facility to site accordign to devicectl
        # facility device allocation

        for device in fac.devices.all():
            for nautobot_device in nautobot_devices:
                if str(nautobot_device.id) == str(device.reference):
                    nautobot.Device().partial_update(nautobot_device, {"site": str(nautobot_site.id)})

    # delete nautobot sites if they no longer exist as facilities in devicectl
    for site in nautobot_sites:

        if not site.custom_fields.devicectl_id:
            continue

        if not models.Facility.objects.filter(id=site.custom_fields.devicectl_id).exists():
            nautobot.Site().destroy(site)

