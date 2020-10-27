import re
from django.utils.translation import gettext_lazy as _

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.schemas.openapi import AutoSchema

from django_devicectl.rest import BadRequest

import django_devicectl.models as models
from django_devicectl.rest.route.devicectl import route

from django_devicectl.rest.serializers.devicectl import Serializers
from django_devicectl.rest.filters import CaseInsensitiveOrderingFilter
from django_devicectl.rest.decorators import grainy_endpoint as _grainy_endpoint, load_object
from django_devicectl.rest.renderers import PlainTextRenderer
from django_devicectl.util import verified_asns

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


class PeeringDBImportSchema(AutoSchema):
    def __init__(self, *args, **kwargs):
        super(AutoSchema, self).__init__(*args, **kwargs)

    def get_operation(self, path, method):
        operation = super().get_operation(path, method)
        operation["responses"] = self._get_responses(path, method)
        return operation

    def _get_operation_id(self, path, method):
        return "ix.import_peeringdb"

    def _get_responses(self, path, method):
        self.response_media_types = self.map_renderers(path, method)
        serializer = Serializers.ix()
        response_schema = self._map_serializer(serializer)
        status_code = "200"

        return {
            status_code: {
                "content": {
                    ct: {"schema": response_schema} for ct in self.response_media_types
                },
                "description": "",
            }
        }


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

@route
class User(viewsets.GenericViewSet):

    """
    List users at the organization
    """

    serializer_class = Serializers.orguser
    queryset = models.OrganizationUser.objects.all()
    ref_tag = "user"

    @grainy_endpoint()
    def list(self, request, org, *args, **kwargs):
        serializer = Serializers.orguser(
            org.user_set.all(),
            many=True,
            context={"user": request.user, "perms": request.perms,},
        )
        return Response(serializer.data)




