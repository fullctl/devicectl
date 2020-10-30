from django.db import models
from django.utils.translation import gettext_lazy as _

import reversion

from django_inet.models import (
    ASNField,
)

import django_peeringdb.models.concrete as pdb_models

from django_grainy.decorators import grainy_model

from fullctl.django.models.concrete import Instance
from fullctl.django.models.abstract import PdbRefModel

import django_devicectl.enum

@reversion.register()
@grainy_model(namespace="net", namespace_instance="net.{instance.org.permission_id}.{instance.asn}")
class Network(PdbRefModel):

    """
    Describes a network

    Can have a reference to a peeringdb netlan object
    """

    name = models.CharField(max_length=255, blank=False)
    asn = ASNField()
    instance = models.ForeignKey(
        Instance, related_name="net_set", on_delete=models.CASCADE, null=True
    )

    class PdbRef(PdbRefModel.PdbRef):
        model = pdb_models.Network
        fields = {"asn": "pdb_id"}

    class HandleRef:
        tag = "net"

    class Meta:
        db_table = "devicectl_net"
        verbose_name_plural = _("Networks")
        verbose_name = _("Network")
        unique_together = (
            ("instance", "asn"),
        )

    @classmethod
    def create_from_pdb(cls, instance, pdb_object, save=True, **fields):

        """
        create instance from peeringdb network

        Argument(s):

        - instance (`Instance`): instance that contains this network
        - pdb_object (`django_peeringdb.Network`): pdb network
        - save (`bool`): if True commit to the database, otherwise dont

        Keyword Argument(s):

        Any arguments passed will be used to set properties on the
        object before creation

        Returns:

        - `Network` instance
        """

        net = super().create_from_pdb(pdb_object, save=save, instance=instance, name=pdb_object.name, asn=pdb_object.asn, **fields)

        return net

    @property
    def display_name(self):
        """
        Will return the exchange name if specified.

        If self.name is not specified and pdb reference is set return
        the name of the peeringdb ix instead

        If peeringdb reference is not specified either, return
        generic "Nameless Exchange ({id})"
        """

        if self.name:
            return self.name
        if self.pdb_id:
            return self.pdb.name
        return f"Unknown Network (AS{self.asn})"

    @property
    def org(self):
        return self.instance.org

    @property
    def members(self):
        if not hasattr(self, "_members"):
            self._members = [
                member for member in
                InternetExchangeMember.objects.filter(
                    asn = self.asn
                )
            ]
        return self._members

    def __str__(self):
        return f"{self.name} (AS{self.asn})"
