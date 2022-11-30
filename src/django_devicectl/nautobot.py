import fullctl.service_bridge.nautobot as nautobot
from django.utils.translation import gettext_lazy as _
from fullctl.django.models.concrete.service_bridge import service_bridge_action

import django_devicectl.models.devicectl as models

# TODO: work around to deal with pagination for now
# Needs to be fixed in fullctl service bridge client to naturally
# support pagination arguments
NAUTOBOT_PAGE_LIMIT = 999999


@service_bridge_action(
    "nautobot_push_device_loc", _("Nautobot: update device location")
)
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
        # TODO: nautobot does not allow a device not connected to a site
        # what to do here?
        # nautobot.Device().partial_update(device.reference.object, {"site": ""})
        return
    facility = device.facility

    # site exists in nautobot?
    site = nautobot.Site().first(cf_devicectl_id=facility.id)

    if site:

        # assign device to site in nautobot
        nautobot.Device().partial_update(
            device.reference.object, {"site": str(site.id)}
        )


@service_bridge_action(
    "nautobot_pull_mgmt_ips", _("Nautobot: retrieve management ip-addresses")
)
def pull_device_mgmt_ips(action, device):

    """
    Pull handler that pulls device management pimary ip addresses
    from nautobot

    Note: this expensive and will significantly slow down API reads for /device
    This is not needed if nautobot is set up to automatically push to devicectl
    """

    # this action only works on pull
    if action != "pull":
        return

    if device.reference_source != "nautobot":
        return

    nautobot_device = device.reference.object

    if not nautobot_device:
        return

    if nautobot_device.primary_ip4:
        device.set_management_ip_address(nautobot_device.primary_ip4.address)

    if nautobot_device.primary_ip6:
        device.set_management_ip_address(nautobot_device.primary_ip6.address)

    pull_interfaces(device)


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


def pull_ip_addresses(virtual_port):

    """
    Pull ip addresses into port infos from nautobot for the specified virtualport
    """

    ip4 = None
    ip6 = None

    for nautobot_ip in nautobot.IPAddress().objects(limit=NAUTOBOT_PAGE_LIMIT):

        if ip4 and ip6:
            break

        if nautobot_ip.assigned_object_id != str(virtual_port.reference):
            continue

        if nautobot_ip.family.value == 4:
            ip4 = nautobot_ip
        elif nautobot_ip.family.value == 6:
            ip6 = nautobot_ip

    if ip4:
        virtual_port.port.port_info.ip_address_4 = (ip4.address, ip4.id)
    else:
        virtual_port.port.port_info.ip_address_4 = None

    if ip6:
        virtual_port.port.port_info.ip_address_6 = (ip6.address, ip6.id)
    else:
        virtual_port.port.port_info.ip_address_6 = None


def pull_interfaces(device):

    """
    Pulls interfaces into virtual ports from nautobot for the specified devices
    """

    for nautobot_if in nautobot.Interface().objects(device_id=str(device.reference)):

        # for now only pull virtual and lag  interfaces

        if nautobot_if.type.value in ["virtual", "lag"]:
            pull_interface(nautobot_if, device)


def pull_interface(nautobot_if, device):

    """
    Pull virtual or LAG interface from nautobot

    Called automatically by `pull_interfaces`
    """

    try:
        virtual_port = models.VirtualPort.objects.get(
            reference=nautobot_if.id, logical_port__physical_ports__device=device
        )
    except models.VirtualPort.DoesNotExist:

        if nautobot_if.type.value == "virtual":
            logical_port = device.physical_ports.first().logical_port
        elif nautobot_if.type.value == "lag":
            logical_port = models.LogicalPort.objects.create(
                name=nautobot_if.display,
                instance=device.instance,
            )
            models.PhysicalPort.objects.create(device=device, logical_port=logical_port)
        virtual_port = models.VirtualPort.objects.create(
            reference=nautobot_if.id,
            vlan_id=0,
            logical_port=logical_port,
            name=nautobot_if.display,
        )

    changed = virtual_port.sync_from_reference(ref_obj=nautobot_if)
    if changed:
        virtual_port.save()

        if nautobot_if.type.value == "lag":
            virtual_port.logical_port.name = virtual_port.name
            virtual_port.logical_port.save()

    try:
        virtual_port.port
    except AttributeError:
        virtual_port.port = models.Port.objects.create(virtual_port=virtual_port)
        virtual_port.save()

    if not virtual_port.port.port_info:
        virtual_port.port.port_info = models.PortInfo.objects.create(
            instance=device.instance
        )
        virtual_port.port.save()

    pull_ip_addresses(virtual_port)


def delete_interfaces():

    """
    Deletes all nautobot referenced virtual ports that not longer
    exist as interfaces in nautobot
    """

    virtual_port_qset = models.VirtualPort.objects.exclude(
        reference__isnull=True
    ).exclude(reference="")

    references = [virtual_port.reference for virtual_port in virtual_port_qset]

    # delete interfaces that no longer exist in nautobot

    qset_remove = models.VirtualPort.objects.exclude(reference__in=references).exclude(
        reference__isnull=True
    )
    qset_remove.delete()


def pull(org, *args, **kwargs):

    """
    Pull data from nautobot
    """

    instance = models.Instance.objects.get(org=org)

    # FIXME allow per organization set up of nautobot url / token
    # currently uses globally configured values for both

    references = []

    # create / update devices from nautobot data

    for nautobot_device in nautobot.Device().objects(limit=NAUTOBOT_PAGE_LIMIT):

        if not nautobot_device.device_role.name.lower().startswith("router"):
            continue

        device, created = models.Device.objects.get_or_create(
            reference=nautobot_device.id, instance=instance
        )
        print(f"[PULL] Nautobot device {nautobot_device.name} {device.reference} ...")
        references.append(device.reference)
        changed = device.sync_from_reference(ref_obj=nautobot_device)

        if changed or created:
            device.save()

        if not device.physical_ports.exists():
            device.setup()

        # pull interfaces

        pull_interfaces(device)

        # assign to facility

        site = nautobot.Site().first(id=nautobot_device.site.id)

        if site.custom_fields.devicectl_id:
            facility = models.Facility.objects.get(id=site.custom_fields.devicectl_id)
            device.facility = facility
            device.save()

        if nautobot_device.primary_ip4:
            device.set_management_ip_address(nautobot_device.primary_ip4.address)

        if nautobot_device.primary_ip6:
            device.set_management_ip_address(nautobot_device.primary_ip6.address)

    # delete devices that no longer exist in nautobot

    qset_remove = models.Device.objects.exclude(reference__in=references).exclude(
        reference__isnull=True
    )

    qset_remove.delete()

    delete_interfaces()


def push(org, *args, **kwargs):

    """
    Push data to nautobot
    """

    # make sure required custom fields exist on the nautobot side

    sync_custom_fields()

    # preload nautobot data

    nautobot_sites = [fac for fac in nautobot.Site().objects(limit=NAUTOBOT_PAGE_LIMIT)]
    # nautobot_devices = [
    #
    #     dev for dev in nautobot.Device().objects(limit=NAUTOBOT_PAGE_LIMIT)
    # ]

    # sync devicectl facility -> nautobot site

    for fac in models.Facility.objects.exclude(slug="pdb"):

        exists = False

        for nautobot_site in nautobot_sites:

            if nautobot_site.custom_fields.devicectl_id == fac.id:
                exists = nautobot_site
                break

        if not exists:
            nautobot_site = nautobot.Site().create(fac.service_bridge_data("nautobot"))
            # nautobot_site = nautobot.Site().object(data["id"])
        else:
            nautobot.Site().update(exists, fac.service_bridge_data("nautobot"))

        # assign nautobot facility to site accordign to devicectl
        # facility device allocation

        # device location managed in nautobot for now. this needs to support stuff like
        # rack location otherwise. TODO: revisit if needed
        # for device in fac.devices.all():
        #    for nautobot_device in nautobot_devices:
        #        if str(nautobot_device.id) == str(device.reference):
        #            nautobot.Device().partial_update(
        #                nautobot_device, {"site": str(nautobot_site.id)}
        #            )

    # delete nautobot sites if they no longer exist as facilities in devicectl
    for site in nautobot_sites:

        if not site.custom_fields.devicectl_id:
            continue

        if not models.Facility.objects.filter(
            id=site.custom_fields.devicectl_id
        ).exists():
            nautobot.Site().destroy(site)
