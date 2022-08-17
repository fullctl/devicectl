import fullctl.service_bridge.nautobot as nautobot
from fullctl.django.models import Task
from fullctl.django.tasks import register

import django_devicectl.models.devicectl as models


@register
class NautobotPull(Task):

    """
    Sync data from nautobot API to devicectl
    """

    class TaskMeta:
        limit = 1

    class Meta:
        proxy = True

    class HandleRef:
        tag = "task_nautobot_pull"

    @property
    def generate_limit_id(self):
        return self.org_id

    def run(self, *args, **kwargs):

        instance = models.Instance.objects.get(org_id=self.org_id)

        # TODO allow per organization set up of nautobot url / token

        for n_device in nautobot.Device().objects():
            device, _ = models.Device.objects.get_or_create(
                reference=n_device.id, instance=instance
            )
            device.name = n_device.display
            device.save()
