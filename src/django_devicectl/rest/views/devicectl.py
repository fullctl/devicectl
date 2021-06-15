import re
from django.utils.translation import gettext_lazy as _

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.schemas.openapi import AutoSchema

from fullctl.django.rest.filters import CaseInsensitiveOrderingFilter
from fullctl.django.rest.decorators import grainy_endpoint as _grainy_endpoint, load_object
from fullctl.django.rest.renderers import PlainTextRenderer
from fullctl.django.rest.core import BadRequest
from fullctl.django.util import verified_asns
from fullctl.django.rest.serializers.org import Serializers as OrgSerializers


import django_devicectl.models as models
from django_devicectl.rest.route.devicectl import route

from django_devicectl.rest.serializers.devicectl import Serializers

class grainy_endpoint(_grainy_endpoint):
    def __init__(self, *args, **kwargs):
        super().__init__(
            instance_class=models.Instance,
            explicit=kwargs.pop("explicit", False),
            *args,
            **kwargs
        )
        if "namespace" not in kwargs:
            self.namespace += ["devicectl"]


@route
class Device(viewsets.GenericViewSet):
    serializer_class = Serializers.device
    queryset = models.Device.objects.all()

    @grainy_endpoint(
        namespace = "device.{request.org.permission_id}"
    )
    def list(self, request, org, instance, *args, **kwargs):
        serializer = Serializers.device(
            instance.device_set.all(),
            many=True,
        )
        return Response(serializer.data)

@route
class PhysicalPort(viewsets.GenericViewSet):
    serializer_class = Serializers.physical_port
    queryset = models.PhysicalPort.objects.all()

    @grainy_endpoint(
        namespace = "physical_port.{request.org.permission_id}"
    )
    def list(self, request, org, instance, *args, **kwargs):
        serializer = Serializers.physical_port(
            self.get_queryset().filter(
                device__instance=instance
            ),
            many=True,
        )
        return Response(serializer.data)



@route
class LogicalPort(viewsets.GenericViewSet):
    serializer_class = Serializers.logical_port
    queryset = models.LogicalPort.objects.all()

    @grainy_endpoint(
        namespace = "logical_port.{request.org.permission_id}"
    )
    def list(self, request, org, instance, *args, **kwargs):
        serializer = Serializers.logical_port(
            instance.logical_port_set.all(),
            many=True,
        )
        return Response(serializer.data)

@route
class VirtualPort(viewsets.GenericViewSet):
    serializer_class = Serializers.virtual_port
    queryset = models.VirtualPort.objects.all()

    @grainy_endpoint(
        namespace = "virtual_port.{request.org.permission_id}"
    )
    def list(self, request, org, instance, *args, **kwargs):
        serializer = Serializers.virtual_port(
            self.get_queryset().filter(logical_port__instance=instance),
            many=True,
        )
        return Response(serializer.data)



class User(viewsets.GenericViewSet):

    """
    List users at the organization
    """

    serializer_class = OrgSerializers.orguser
    queryset = models.OrganizationUser.objects.all()
    ref_tag = "user"

    @grainy_endpoint()
    def list(self, request, org, *args, **kwargs):
        serializer = OrgSerializers.orguser(
            org.user_set.all(),
            many=True,
            context={"user": request.user, "perms": request.perms,},
        )
        return Response(serializer.data)




