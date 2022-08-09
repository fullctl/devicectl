# Settings

- `NAUTOBOT_URL`: url of the nautobot instance
- `NAUTOBOT_TOKEN`: api token to use for authentication
  - The token can be created through nautobot admin interface
  - The token needs full permissions to the following models:
    - `dcim | device`
    - `dcim | device type`
    - `dcim | site`
    - `extras | custom field`

- `SERVICE_BRIDGE_REF_DEVICE`: set to `fullctl.service_bridge.nautobot.Device` to tell devicectl that nautobot is the source of truth for devices.

## Sync changes from nautobot to devicectl

### 1. Run `devicectl_nautobot_pull` job

```sh
python manage.py devicectl_nautobot_pull {org.slug} --commit
```

### 2. Set up nautobot fullctl integration

Install the [nautobot_fullctl](https://github.com/fullctl/nautobot_fullctl) addon into nautobot.

Aftewards device changes will be synced directly to devicectl from nautobot using the service bridge.

!!! Add device to facility manually

Currently nautobot device locations are not synced. If your devicectl devices list is empty after a sync, it likely means
that you will still need to assign the device to the facility in devicectl. To do this click `Add device` in devicectl.

## Sync changes from devicectl to nautobot

currently work in progress and not available at this point
