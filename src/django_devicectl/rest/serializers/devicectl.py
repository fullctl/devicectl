try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

import yaml

from django.utils.translation import ugettext_lazy as _
from django.core.validators import RegexValidator

from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.validators import UniqueTogetherValidator

from django_inet.rest import IPAddressField

import django_peeringdb.models.concrete as pdb_models

from fullctl.django.rest.decorators import serializer_registry
from fullctl.django.rest.serializers import RequireContext, ModelSerializer


import django_devicectl.models as models

Serializers, register = serializer_registry()

@register
class Device(ModelSerializer):
    class Meta:
        model = models.Device
        fields = ["name", "type", "description"]


@register
class PhysicalPort(ModelSerializer):
    class Meta:
        model = models.PhysicalPort
        fields = ["device", "name", "logport", "description"]


@register
class LogicalPort(ModelSerializer):
    class Meta:
        model = models.LogicalPort
        fields = ["name", "trunk", "channel", "description"]


@register
class VirtualPort(ModelSerializer):
    class Meta:
        model = models.VirtualPort
        fields = ["logport", "vlan_id"]
