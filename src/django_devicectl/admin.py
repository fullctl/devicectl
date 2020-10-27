from django.contrib import admin
from django.utils.translation import gettext as _
from django_handleref.admin import VersionAdmin

from django_devicectl.models import (
    Organization,
    OrganizationUser,
    APIKey,
)


class BaseAdmin(VersionAdmin):
    readonly_fields = ("version",)


class BaseTabularAdmin(admin.TabularInline):
    readonly_fields = ("version",)


@admin.register(APIKey)
class APIKeyAdmin(BaseAdmin):
    list_display = ("id", "user", "key")


class OrganizationUserInline(admin.TabularInline):
    model = OrganizationUser
    extra = 0
    fields = ("status", "user")


@admin.register(Organization)
class OrganizationAdmin(BaseAdmin):
    list_display = ("id", "name", "slug")
    inlines = (OrganizationUserInline,)
