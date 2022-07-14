from fullctl.django.auditlog import auditlog
from fullctl.django.rest.api_schema import PeeringDBImportSchema
from fullctl.django.rest.core import BadRequest
from fullctl.django.rest.decorators import billable, load_object
from fullctl.django.rest.filters import CaseInsensitiveOrderingFilter
from fullctl.django.rest.mixins import CachedObjectMixin, OrgQuerysetMixin
from fullctl.django.rest.renderers import PlainTextRenderer
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

import django_devicectl.models as models
from django_devicectl.rest.decorators import grainy_endpoint
from django_devicectl.rest.route.devicectl import route
from django_devicectl.rest.serializers.devicectl import Serializers


@route
class Device(CachedObjectMixin, viewsets.GenericViewSet):
    serializer_class = Serializers.device
    queryset = models.Device.objects.all()
    lookup_url_kwarg = "device_id"
    ref_tag = "device"
    lookup_field = "id"

    @grainy_endpoint(namespace="device.{request.org.permission_id}")
    def list(self, request, org, instance, *args, **kwargs):
        ordering_filter = CaseInsensitiveOrderingFilter(["name", "type"])

        queryset = instance.device_set.all()
        queryset = ordering_filter.filter_queryset(request, queryset, self)

        serializer = Serializers.device(
            queryset,
            many=True,
        )
        return Response(serializer.data)

    @grainy_endpoint(namespace="device.{request.org.permission_id}.{device_pk}")
    @load_object("device", models.Device, instance="instance", id="device_id")
    def retrieve(self, request, org, instance, device, *args, **kwargs):
        serializer = Serializers.device(
            instance=device,
            many=False,
        )
        return Response(serializer.data)

    @auditlog()
    @grainy_endpoint(namespace="device.{request.org.permission_id}")
    def create(self, request, org, instance, *args, **kwargs):
        data = request.data
        data["instance"] = instance.id
        serializer = Serializers.device(data=data)
        if not serializer.is_valid():
            return BadRequest(serializer.errors)
        device = serializer.save()
        device.save()

        return Response(Serializers.device(instance=device).data)

    @auditlog()
    @grainy_endpoint(namespace="device.{request.org.permission_id}.{device_id}")
    @load_object("device", models.Device, instance="instance", id="device_id")
    def update(self, request, org, instance, device, *args, **kwargs):
        request.data["instance"] = instance.id
        serializer = Serializers.device(
            device,
            data=request.data,
        )

        if not serializer.is_valid():
            return BadRequest(serializer.errors)
        device = serializer.save()
        device.save()

        return Response(Serializers.device(instance=device).data)

    @auditlog()
    @grainy_endpoint(namespace="device.{request.org.permission_id}.{device_id}")
    @load_object("device", models.Device, instance="instance", id="device_id")
    def destroy(self, request, org, instance, device, *args, **kwargs):
        r = Response(Serializers.device(instance=device).data)
        device.delete()
        return r


@route
class PhysicalPort(CachedObjectMixin, viewsets.GenericViewSet):
    serializer_class = Serializers.physical_port
    queryset = models.PhysicalPort.objects.all()

    lookup_url_kwarg = "physical_port_id"
    ref_tag = "physical_port"
    lookup_field = "id"

    @grainy_endpoint(namespace="physical_port.{request.org.permission_id}")
    def list(self, request, org, instance, *args, **kwargs):
        ordering_filter = CaseInsensitiveOrderingFilter(
            ["name", "device", "logical_port"]
        )

        queryset = self.get_queryset().filter(device__instance=instance)
        queryset = ordering_filter.filter_queryset(request, queryset, self)

        serializer = Serializers.physical_port(queryset, many=True)
        return Response(serializer.data)

    @grainy_endpoint(
        namespace="physical_port.{request.org.permission_id}.{physical_port_pk}"
    )
    @load_object(
        "physical_port",
        models.PhysicalPort,
        device__instance="instance",
        id="physical_port_id",
    )
    def retrieve(self, request, org, instance, physical_port, *args, **kwargs):
        serializer = Serializers.physical_port(
            instance=physical_port,
            many=False,
        )
        return Response(serializer.data)

    @auditlog()
    @grainy_endpoint(namespace="physical_port.{request.org.permission_id}")
    def create(self, request, org, instance, *args, **kwargs):
        device = models.Device.objects.get(
            instance=instance, id=request.data.get("device")
        )
        serializer = Serializers.physical_port(data=request.data)
        if not serializer.is_valid():
            return BadRequest(serializer.errors)
        physical_port = serializer.save()
        physical_port.save()

        return Response(Serializers.physical_port(instance=physical_port).data)

    @auditlog()
    @grainy_endpoint(
        namespace="physical_port.{request.org.permission_id}.{physical_port_id}"
    )
    @load_object(
        "physical_port",
        models.PhysicalPort,
        device__instance="instance",
        id="physical_port_id",
    )
    def update(self, request, org, instance, physical_port, *args, **kwargs):
        serializer = Serializers.physical_port(
            physical_port,
            data=request.data,
        )

        if not serializer.is_valid():
            return BadRequest(serializer.errors)
        physical_port = serializer.save()
        physical_port.save()

        return Response(Serializers.physical_port(instance=physical_port).data)

    @auditlog()
    @grainy_endpoint(
        namespace="physical_port.{request.org.permission_id}.{physical_port_id}"
    )
    @load_object(
        "physical_port",
        models.PhysicalPort,
        device__instance="instance",
        id="physical_port_id",
    )
    def destroy(self, request, org, instance, physical_port, *args, **kwargs):
        r = Response(Serializers.physical_port(instance=physical_port).data)
        physical_port.delete()
        return r


@route
class LogicalPort(CachedObjectMixin, viewsets.GenericViewSet):
    serializer_class = Serializers.logical_port
    queryset = models.LogicalPort.objects.all()
    lookup_url_kwarg = "logical_port_id"
    ref_tag = "logical_port"
    lookup_field = "id"

    @grainy_endpoint(namespace="logical_port.{request.org.permission_id}")
    def list(self, request, org, instance, *args, **kwargs):
        ordering_filter = CaseInsensitiveOrderingFilter(["name", "channel", "trunk"])

        queryset = instance.logical_port_set.all()
        queryset = ordering_filter.filter_queryset(request, queryset, self)

        serializer = Serializers.logical_port(
            queryset,
            many=True,
        )
        return Response(serializer.data)

    @grainy_endpoint(
        namespace="logical_port.{request.org.permission_id}.{logical_port_pk}"
    )
    @load_object(
        "logical_port", models.LogicalPort, instance="instance", id="logical_port_id"
    )
    def retrieve(self, request, org, instance, logical_port, *args, **kwargs):
        serializer = Serializers.logical_port(
            instance=logical_port,
            many=False,
        )
        return Response(serializer.data)

    @auditlog()
    @grainy_endpoint(namespace="logical_port.{request.org.permission_id}")
    def create(self, request, org, instance, *args, **kwargs):
        request.data["instance"] = instance.id
        serializer = Serializers.logical_port(data=request.data)
        if not serializer.is_valid():
            return BadRequest(serializer.errors)
        logical_port = serializer.save()
        logical_port.save()

        return Response(Serializers.logical_port(instance=logical_port).data)

    @auditlog()
    @grainy_endpoint(
        namespace="logical_port.{request.org.permission_id}.{logical_port_id}"
    )
    @load_object(
        "logical_port", models.LogicalPort, instance="instance", id="logical_port_id"
    )
    def update(self, request, org, instance, logical_port, *args, **kwargs):
        request.data["instance"] = instance.id
        serializer = Serializers.logical_port(
            logical_port,
            data=request.data,
        )

        if not serializer.is_valid():
            return BadRequest(serializer.errors)
        logical_port = serializer.save()
        logical_port.save()

        return Response(Serializers.logical_port(instance=logical_port).data)

    @auditlog()
    @grainy_endpoint(
        namespace="logical_port.{request.org.permission_id}.{logical_port_id}"
    )
    @load_object(
        "logical_port", models.LogicalPort, instance="instance", id="logical_port_id"
    )
    def destroy(self, request, org, instance, logical_port, *args, **kwargs):
        r = Response(Serializers.logical_port(instance=logical_port).data)
        logical_port.delete()
        return r


@route
class VirtualPort(CachedObjectMixin, viewsets.GenericViewSet):
    serializer_class = Serializers.virtual_port
    queryset = models.VirtualPort.objects.all()
    lookup_url_kwarg = "virtual_port_id"
    ref_tag = "virtual_port"
    lookup_field = "id"

    @grainy_endpoint(namespace="virtual_port.{request.org.permission_id}")
    def list(self, request, org, instance, *args, **kwargs):

        ordering_filter = CaseInsensitiveOrderingFilter(
            ["name", "vlan_id", "logical_port"]
        )

        queryset = self.get_queryset().filter(logical_port__instance=instance)
        queryset = queryset.select_related("logical_port")
        queryset = ordering_filter.filter_queryset(request, queryset, self)

        serializer = Serializers.virtual_port(
            queryset,
            many=True,
        )
        return Response(serializer.data)

    @grainy_endpoint(
        namespace="virtual_port.{request.org.permission_id}.{virtual_port_pk}"
    )
    @load_object(
        "virtual_port",
        models.VirtualPort,
        logical_port__instance="instance",
        id="virtual_port_id",
    )
    def retrieve(self, request, org, instance, virtual_port, *args, **kwargs):
        serializer = Serializers.virtual_port(
            instance=virtual_port,
            many=False,
        )
        return Response(serializer.data)

    @auditlog()
    @grainy_endpoint(namespace="virtual_port.{request.org.permission_id}")
    def create(self, request, org, instance, *args, **kwargs):
        models.LogicalPort.objects.get(
            instance=instance, id=request.data.get("logical_port")
        )
        serializer = Serializers.virtual_port(data=request.data)
        if not serializer.is_valid():
            return BadRequest(serializer.errors)
        virtual_port = serializer.save()
        virtual_port.save()

        return Response(Serializers.virtual_port(instance=virtual_port).data)

    @auditlog()
    @grainy_endpoint(
        namespace="virtual_port.{request.org.permission_id}.{virtual_port_id}"
    )
    @load_object(
        "virtual_port",
        models.VirtualPort,
        logical_port__instance="instance",
        id="virtual_port_id",
    )
    def update(self, request, org, instance, virtual_port, *args, **kwargs):
        serializer = Serializers.virtual_port(
            virtual_port,
            data=request.data,
        )

        if not serializer.is_valid():
            return BadRequest(serializer.errors)
        virtual_port = serializer.save()
        virtual_port.save()

        return Response(Serializers.virtual_port(instance=virtual_port).data)

    @auditlog()
    @grainy_endpoint(
        namespace="virtual_port.{request.org.permission_id}.{virtual_port_id}"
    )
    @load_object(
        "virtual_port",
        models.VirtualPort,
        logical_port__instance="instance",
        id="virtual_port_id",
    )
    def destroy(self, request, org, instance, virtual_port, *args, **kwargs):
        r = Response(Serializers.virtual_port(instance=virtual_port).data)
        virtual_port.delete()
        return r
