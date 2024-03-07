import fullctl.service_bridge.netbox as netbox
import django_devicectl.models.devicectl as models



NETBOX_PAGE_LIMIT = 999999


def sync_custom_fields():
    """
    Make sure the necessary custom fields exist in netbox
    """


    netbox.CustomField().sync(
        [
            {
                "name": "devicectl_id",
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
    Push data to netbox
    """
    # make sure required custom fields exist on the netbox side

    sync_custom_fields()

    # preload netbox data

    netbox_sites = [fac for fac in netbox.Site().objects(limit=NETBOX_PAGE_LIMIT)]

    # sync devicectl facility -> netbox site

    for fac in models.Facility.objects.exclude(slug="pdb").exclude(slug="peerctl"):
        exists = False

        for netbox_site in netbox_sites:
            # check if id match exists
            if netbox_site.custom_fields.devicectl_id == fac.id:
                exists = netbox_site
                break

        if not exists:
            # check if slug match exists
            for netbox_site in netbox_sites:
                if netbox_site.slug.lower() == fac.slug.lower():
                    exists = netbox_site
                    break

        if not exists:
            # site does not exist (searched slug and devicectl reference id matches)
            # create it

            netbox_site = netbox_site.Site().create(fac.service_bridge_data("netbox"))

        else:
            # site exists (searched slug and devicectl reference id matches)
            # update it

            netbox_site.Site().update(exists, fac.service_bridge_data("netbox"))

    # delete netbox sites if they no longer exist as facilities in devicectl
    for site in netbox_sites:
        if not site.custom_fields.devicectl_id:
            continue

        if not models.Facility.objects.filter(
            id=site.custom_fields.devicectl_id
        ).exists():
            netbox.Site().destroy(site)
