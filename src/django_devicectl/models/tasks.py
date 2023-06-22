import os

import fullctl.graph.mrtg.rrd as mrtg_rrd
import fullctl.service_bridge.nautobot as nautobot
import fullctl.service_bridge.peerctl as peerctl
from django.conf import settings
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


@register
class RequestPeerctlSync(Task):
    """
    Will request peerctl to sync devices and ports from devicectl
    """

    class TaskMeta:
        limit = 1

    class Meta:
        proxy = True

    class HandleRef:
        tag = "task_request_peerctl_sync"

    @property
    def generate_limit_id(self):
        return self.org_id

    def run(self, *args, **kwargs):
        net = peerctl.Network()
        url = f"{net.url_prefix}/{net.ref_tag}/request_devicectl_sync"
        net.post(url, json={"org_id": self.org.remote_id})


@register
class UpdateTrafficGraphs(Task):
    """
    Will update traffic graphs

    Required keyword parameters for `create_task` are

    - `context_model`: `virtual_port` or `physical_port`

    Optional keyword parameters for `create_task` are

    - `update`: list of dicts with keys `id`, `bps_in`, `bps_out`, `bps_in_max`, `bps_out_max`, `timestamp`
    - `import_mrtg`: list of dicts with keys `id`, `log_lines`
    """

    class Meta:
        proxy = True

    class HandleRef:
        tag = "task_update_virtual_port_traffic_graphs"

    @property
    def context_model(self):
        """
        Returns the context model class based on ref tag value stored
        in the task instance's `param['kwargs']['context_model']` field.
        """

        ref_tag = self.param["kwargs"]["context_model"]

        if ref_tag == "virtual_port":
            return models.VirtualPort
        elif ref_tag == "physical_port":
            return models.PhysicalPort
        else:
            raise ValueError(f"Unknown context model {ref_tag}")

    def run(self, *args, **kwargs):
        for data in kwargs.get("update", []):
            self.update_rrd(data)

        for data in kwargs.get("import_mrtg", []):
            self.import_mrtg(data)

    def update_rrd(self, data):
        """
        Update the RRD file for the given context object with the given data point (single data point)
        """

        context_obj = self.context_model.objects.get(id=data["id"])
        bps_in = data["bps_in"]
        bps_out = data["bps_out"]
        timestamp = data["timestamp"]
        bps_in_max = data["bps_in_max"]
        bps_out_max = data["bps_out_max"]

        if not context_obj.meta or "graph" not in context_obj.meta:
            graph_file = f"{context_obj.HandleRef.tag}-{context_obj.id}.rrd"
        else:
            graph_file = context_obj.meta["graph"]

        graph_path = os.path.join(settings.GRAPHS_PATH, graph_file)

        if not os.path.exists(graph_path):
            mrtg_rrd.create_rrd_file(graph_path, timestamp)

        mrtg_rrd.update_rrd(
            graph_path,
            f"{timestamp} {bps_in} {bps_out} {bps_in_max} {bps_out_max}",
            mrtg_rrd.get_last_update_time(graph_path),
        )

        context_obj.meta["graph"] = graph_file
        context_obj.save()

    def import_mrtg(self, data):
        """
        Import MRTG log lines into RRD file for the given context object
        """

        context_obj = self.context_model.objects.get(id=data["id"])

        # check if graph file already exists

        if not context_obj.meta or "graph" not in context_obj.meta:
            graph_file = f"{context_obj.HandleRef.tag}-{context_obj.id}.rrd"
        else:
            graph_file = context_obj.meta["graph"]

        graph_path = os.path.join(settings.GRAPHS_PATH, graph_file)

        if os.path.exists(graph_path):
            os.remove(graph_path)

        log_lines = data["log_lines"]

        log_lines.reverse()

        for log_line in log_lines:
            print(log_line)

        mrtg_rrd.stream_log_lines_to_rrd(graph_path, log_lines)

        context_obj.meta["graph"] = graph_file
        context_obj.save()
