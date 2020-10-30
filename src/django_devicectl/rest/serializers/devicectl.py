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
class Network(ModelSerializer):
    class Meta:
        model = models.Network
        fields = ["pdb_id", "asn", "name", "display_name"]


