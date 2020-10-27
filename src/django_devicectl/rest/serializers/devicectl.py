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

import django_devicectl.models as models

import django_peeringdb.models.concrete as pdb_models

from django_devicectl.rest.decorators import serializer_registry
from django_devicectl.rest.serializers import RequireContext, ModelSerializer

from django_inet.rest import IPAddressField


Serializers, register = serializer_registry()


class SoftRequiredValidator:
    """
    A validator that allows us to require that at least
    one of the specified fields is set
    """

    message = _("This field is required")
    requires_context = True

    def __init__(self, fields, message=None):
        self.fields = fields
        self.message = message or self.message

    def set_context(self, serializer):
        self.instance = getattr(serializer, "instance", None)

    def __call__(self, attrs, serializer):
        missing = {
            field_name: self.message
            for field_name in self.fields
            if not attrs.get(field_name)
        }
        valid = len(self.fields) != len(missing.keys())
        if not valid:
            raise ValidationError(missing)


@register
class Network(ModelSerializer):
    class Meta:
        model = models.Network
        fields = ["pdb_id", "asn", "name", "display_name"]


@register
class OrganizationUser(ModelSerializer):
    ref_tag = "orguser"

    name = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    you = serializers.SerializerMethodField()

    class Meta:
        model = models.OrganizationUser
        fields = ["id", "name", "email", "you"]

    def get_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"

    def get_email(self, obj):
        return obj.user.email

    def get_you(self, obj):
        return obj.user == self.context.get("user")
