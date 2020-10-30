from django_grainy.helpers import int_flags
from django.conf import settings
import django_peeringdb.models.concrete as pdb_models

"""
def sync_organizations(backend, details, response, uid, user, *args, **kwargs):
    social = kwargs.get("social") or backend.strategy.storage.user.get_social_auth(
        backend.name, uid
    )
    if social and settings.MANAGED_BY_OAUTH:
        organizations = social.extra_data.get("organizations", [])
        Organization.sync(organizations, user, backend.name)

"""
