from django.urls import include, path

import django_devicectl.rest.route.devicectl
import django_devicectl.rest.views.devicectl

urlpatterns = [
    path("", include(django_devicectl.rest.route.devicectl.router.urls)),
]
