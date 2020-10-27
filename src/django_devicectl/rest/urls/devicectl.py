from django.urls import path, include

import django_devicectl.rest.views.devicectl
import django_devicectl.rest.route.devicectl

urlpatterns = [
    path("", include(django_devicectl.rest.route.devicectl.router.urls)),
]
