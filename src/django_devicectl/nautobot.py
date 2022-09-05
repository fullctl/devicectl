import fullctl.service_bridge.nautobot as nautobot

import django_devicectl.models.devicectl as models


def pull(org, *args, **kwargs):

    instance = models.Instance.objects.get(org=org)

    # FIXME allow per organization set up of nautobot url / token
    # currently uses globally configured values for both

    references = []

    for nautobot_device in nautobot.Device().objects():
        device, created = models.Device.objects.get_or_create(
            reference=nautobot_device.id, instance=instance
        )
        print(f"Syncing {nautobot_device.name} from nautobot")
        references.append(device.reference)
        changed = device.sync_from_reference(ref_obj=nautobot_device)

        if changed or created:
            device.save()

    # delete devices that no longer exist in nautobot
    qset_remove = models.Device.objects.exclude(reference__in=references).exclude(
        reference__isnull=True
    )

    print(f"Removing {qset_remove.count()} devices..")

    qset_remove.delete()


def sync_custom_fields():

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


def push(org, *args, **kwargs):

    """
    Pushes changes to nautobot using the service bridge
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

        # XXX
        # delete nautobot sites if they no longer exist as facilities in devicectl?
