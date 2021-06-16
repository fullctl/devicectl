from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView
from django.conf import settings

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
