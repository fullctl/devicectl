import fullctl.service_bridge.nautobot as nautobot

import django_devicectl.models.devicectl as models

DEVICE_MAP = {
    "display": "name"
}

def apply_changes(nautobot_object, fullctl_object, field_map):
    changed = False
    for nautobot_field, fullctl_field in field_map.items():
        nautobot_value = getattr(nautobot_object, nautobot_field)
        fullctl_value = getattr(fullctl_object, fullctl_field)
        if nautobot_value != fullctl_value:
            setattr(fullctl_object, fullctl_field, nautobot_value)
            changed = True
    return changed

def pull(org, *args, **kwargs):

    instance = models.Instance.objects.get(org=org)

    # FIXME allow per organization set up of nautobot url / token
    # currently uses globally configured values for both

    for nautobot_device in nautobot.Device().objects():
        device, created = models.Device.objects.get_or_create(reference=nautobot_device.id, instance=instance)

        if apply_changes(nautobot_device, device, DEVICE_MAP) or created:
            print("saving device", device)
            device.save()
