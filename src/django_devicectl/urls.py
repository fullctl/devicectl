from django.conf import settings
from django.contrib.auth import views as auth_views
from django.urls import include, path
from django.views.generic import TemplateView

import django_devicectl.views as views

urlpatterns = [
    path(
        "api/<str:org_tag>/",
        include(
            ("django_devicectl.rest.urls.devicectl", "devicectl_api"),
            namespace="devicectl_api",
        ),
    ),
    path("<str:org_tag>/", views.view_instance, name="devicectl-home"),
]
