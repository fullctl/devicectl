import re
from django.utils.translation import gettext_lazy as _

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.schemas.openapi import AutoSchema

from django_devicectl.rest import BadRequest

from fullctl.django.rest.filters import CaseInsensitiveOrderingFilter
from fullctl.django.rest.decorators import grainy_endpoint as _grainy_endpoint, load_object
from fullctl.django.rest.renderers import PlainTextRenderer
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
class Network(viewsets.GenericViewSet):
    serializer_class = Serializers.net
    queryset = models.Network.objects.all()

    lookup_url_kwarfs = "asn"


    @grainy_endpoint(
        namespace = "net.{request.org.permission_id}"
    )
    def list(self, request, org, instance, *args, **kwargs):
        serializer = Serializers.net(
            instance.net_set.all(),
            many=True,
        )
        return Response(serializer.data)

    @action(
        detail=False, methods=["GET"], url_path="presence/(?P<asn>[\d]+)"
    )
    @grainy_endpoint(
        namespace = "net.{request.org.permission_id}.{asn}"
    )
    @load_object("net", models.Network, asn="asn", instance="instance")
    def presence(self, request, org, instance, asn, net=None, *args, **kwargs):
        serializer = Serializers.presence(
            net.members,
            many=True,
            context={"perms": request.perms, "user": request.user}
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




