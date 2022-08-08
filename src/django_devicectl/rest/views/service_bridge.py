from fullctl.django.rest.route.service_bridge import route
from fullctl.django.rest.views.service_bridge import (  # MethodFilter,
    DataViewSet,
    HeartbeatViewSet,
    StatusViewSet,
)

import django_devicectl.models.devicectl as models
from django_devicectl.rest.serializers.service_bridge import Serializers


@route
class Status(StatusViewSet):
    checks = ("bridge_peerctl", "bridge_aaactl", "bridge_pdbctl")


@route
class Heartbeat(HeartbeatViewSet):
    pass


@route
class Device(DataViewSet):

    path_prefix = "/data"
    allowed_http_methods = ["GET"]
    valid_filters = [
        ("org", "org_id"),
        ("q", "name__icontains"),
        ("ref", "reference"),
    ]
    autocomplete = "name"
    allow_unfiltered = True

    queryset = models.Device.objects.filter(status="ok")
    serializer_class = Serializers.device
