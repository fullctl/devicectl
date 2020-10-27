from django.http import Http404, HttpResponse
from django.conf import settings
from django.shortcuts import render, redirect

import django_devicectl.forms

from django_devicectl.models import (
    Instance,
    Organization,
)

from django_devicectl.decorators import (
    load_instance,
    require_auth,
)

# Create your views here.


def make_env(request, **kwargs):
    r = {"env": settings.RELEASE_ENV, "version": settings.PACKAGE_VERSION}
    r.update(**kwargs)
    return r


@require_auth()
@load_instance()
def view_instance(request, instance, **kwargs):
    env = make_env(request, instance=instance, org=instance.org)
    env["forms"] = {"import_ix": django_devicectl.forms.ImportIXForm()}

    return render(request, "devicectl/index.html", env)


@require_auth()
def org_redirect(request):
    return redirect(f"/{request.org.slug}/")
