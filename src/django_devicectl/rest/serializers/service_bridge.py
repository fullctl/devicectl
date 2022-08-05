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
            "name",
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

