from fullctl.django.rest.route.service_bridge import route
from fullctl.django.rest.views.service_bridge import (  # MethodFilter,
    DataViewSet,
    HeartbeatViewSet,
    StatusViewSet,
)
from rest_framework.decorators import action
from rest_framework.response import Response

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
    allowed_http_methods = ["GET", "POST", "PUT", "DELETE"]
    valid_filters = [
        ("org", "org__remote_id"),
        ("org_slug", "instance__org__slug"),
        ("q", "name__icontains"),
        ("name", "name__iexact"),
        ("ref", "reference"),
        ("port", "physical_ports__logical_port__virtual_ports__port__in"),
    ]
    autocomplete = "name"
    allow_unfiltered = True

    queryset = models.Device.objects.filter(status="ok")
    serializer_class = Serializers.device

    def after_create(self, obj, data):
        obj.setup()


@route
class Port(DataViewSet):

    path_prefix = "/data"
    allowed_http_methods = ["GET"]
    valid_filters = [
        ("org", "virtual_port__logical_port__instance__org__remote_id"),
        ("device", "virtual_port__logical_port__physical_ports__device_id"),
    ]
    allow_unfiltered = True

    queryset = models.Port.objects.filter(status="ok")
    serializer_class = Serializers.port

    @action(
        detail=False, methods=["POST"], serializer_class=Serializers.request_dummy_ports
    )
    def request_dummy_ports(self, request, *args, **kwargs):

        data = self.prepare_write_data(request)

        slz = self.serializer_class(data=data)
        slz.is_valid(raise_exception=True)

        ports = slz.save()

        return Response(Serializers.port(ports, many=True).data)


@route
class Portinfo(DataViewSet):

    path_prefix = "/data"
    allowed_http_methods = ["GET"]
    valid_filters = [
        ("org", "instance__org__remote_id"),
    ]
    allow_unfiltered = True

    queryset = models.PortInfo.objects.filter(status="ok")
    serializer_class = Serializers.port_info


@route
class VirtualPort(DataViewSet):

    path_prefix = "/data"
    allowed_http_methods = ["GET"]
    valid_filters = [
        ("ref", "reference"),
        ("org", "port__port_info__instance__org__remote_id"),
    ]
    allow_unfiltered = True

    queryset = models.VirtualPort.objects.filter(status="ok")
    serializer_class = Serializers.virtual_port


@route
class IPAddress(DataViewSet):

    path_prefix = "/data"
    allowed_http_methods = ["GET"]
    valid_filters = [
        ("ref", "reference"),
        ("org", "instance__org__remote_id"),
    ]
    allow_unfiltered = True

    queryset = models.IPAddress.objects.filter(status="ok")
    serializer_class = Serializers.ip
