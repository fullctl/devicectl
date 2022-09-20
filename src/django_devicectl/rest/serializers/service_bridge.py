from fullctl.django.rest.decorators import serializer_registry
from fullctl.django.rest.serializers import ModelSerializer
from rest_framework import serializers

import django_devicectl.models.devicectl as models

Serializers, register = serializer_registry()


@register
class Device(ModelSerializer):

    org_id = serializers.SerializerMethodField()

    class Meta:
        model = models.Device
        fields = [
            "id",
            "name",
            "display_name",
            "reference",
            "reference_is_sot",
            "description",
            "status",
            "type",
            "instance",
            "org_id",
        ]

    def get_org_id(self, device):
        return device.instance.org.permission_id


@register
class Port(ModelSerializer):

    org_id = serializers.SerializerMethodField()

    ip_address_4 = serializers.CharField(read_only=True, source="port_info.ip_address_4")
    ip_address_6 = serializers.CharField(read_only=True, source="port_info.ip_address_6")
    is_management= serializers.BooleanField(read_only=True, source="port_info.is_management")

    class Meta:
        model = models.Port
        fields = [
            "id",
            "org_id",
            "virtual_port",
            "port_info",
            "display_name",
            "device_id",
            "device_name",
            "name",
            "ip_address_4",
            "ip_address_6",
            "is_management",
        ]

    def get_org_id(self, port):
        return port.org.permission_id

@register
class PortInfo(ModelSerializer):

    org_id = serializers.SerializerMethodField()

    class Meta:
        model = models.PortInfo
        fields = [
            "id",
            "org_id",
            "port",
            "ip_address_4",
            "ip_address_6",
            "is_management",
            "is_routeserver_peer",
            "speed",
            "display_name",
        ]

    def get_org_id(self, port_info):
        return port_info.org.permission_id


@register
class RequestDummyPorts(serializers.Serializer):

    ref_tag = "request_dummy_ports"

    instance = serializers.IntegerField()
    ports = serializers.JSONField()
    name_prefix = serializers.CharField()
    device_type = serializers.CharField()

    class Meta:
        fields = ["ports", "name_prefix", "instance", "device_type"]

    def create(self, validated_data):

        ports = validated_data["ports"]
        instance = models.Instance.objects.get(id=validated_data["instance"])
        name_prefix = validated_data["name_prefix"]
        device_type = validated_data["device_type"]

        created_ports = []

        for device_id, port_data in ports.items():
            device, _ = models.Device.objects.get_or_create(
                name=f"{name_prefix}:{device_id}",
                instance=instance,
                type=device_type
            )
            device.setup()

            virtual_port = device.virtual_ports.first()


            for _port in port_data:
                port, port_created = models.Port.objects.get_or_create(virtual_port=virtual_port, name=f"{name_prefix}:{_port['id']}")
                if port_created or not port.port_info_id:
                    port.port_info = models.PortInfo.objects.create(
                        instance=instance,
                        ip_address_4=_port.get("ip_address_4"),
                        ip_address_6=_port.get("ip_address_6"),
                    )
                    port.save()
                created_ports.append(port)

        return created_ports



