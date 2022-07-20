try:
    from yaml import CDumper as Dumper
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader, Dumper

import yaml
from django.core.validators import RegexValidator
from django.utils.translation import ugettext_lazy as _
from django_inet.rest import IPAddressField
from fullctl.django.rest.decorators import serializer_registry
from fullctl.django.rest.serializers import ModelSerializer, RequireContext
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.validators import UniqueTogetherValidator

import django_devicectl.models as models

Serializers, register = serializer_registry()


@register
class Facility(ModelSerializer):
    class Meta:
        model = models.Facility
        fields = ["id", "name", "address1", "city", "country", "floor", "suite", "zipcode", "reference", "instance"]

@register
class Device(ModelSerializer):
    facility_name = serializers.SerializerMethodField()
    class Meta:
        model = models.Device
        fields = ["name", "display_name", "type", "facility", "facility_name", "reference", "description", "instance"]

    def get_facility_name(self, obj):
        if obj.facility is None:
            return None
        return obj.facility.name


@register
class PhysicalPort(ModelSerializer):
    class Meta:
        model = models.PhysicalPort
        fields = [
            "device",
            "device_name",
            "name",
            "display_name",
            "logical_port",
            "logical_port_name",
            "description",
        ]


@register
class LogicalPort(ModelSerializer):
    class Meta:
        model = models.LogicalPort
        fields = ["name", "display_name", "trunk", "channel", "description", "instance"]


@register
class VirtualPort(ModelSerializer):
    class Meta:
        model = models.VirtualPort
        fields = [
            "name",
            "display_name",
            "logical_port",
            "logical_port_name",
            "vlan_id",
        ]


@register
class PeeringDBFacility(serializers.Serializer):
    ref_tag = "pdbfacility"

    id = serializers.IntegerField()
    name = serializers.CharField(read_only=True)
    address1 = serializers.CharField(read_only=True)
    country = serializers.CharField(read_only=True)
    zipcode = serializers.CharField(read_only=True)
    city = serializers.CharField(read_only=True)
    suite = serializers.CharField(read_only=True)
    floor = serializers.CharField(read_only=True)
    latidude = serializers.DecimalField(read_only=True, max_digits=9, decimal_places=6)
    longitude = serializers.DecimalField(read_only=True, max_digits=9, decimal_places=6)


    class Meta:
        fields = ["id", "name"]

    def get_router_id(self, obj):
        return obj.ipaddr4 or ""
