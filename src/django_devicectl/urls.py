from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView
from django.conf import settings


import django_devicectl.views as views
import django_devicectl.autocomplete.views

urlpatterns = [
    path(
        "api/account/",
        include(
            ("django_devicectl.rest.urls.account", "devicectl_account_api"),
            namespace="devicectl_account_api",
        ),
    ),
    path(
        "api/<str:org_tag>/",
        include(("django_devicectl.rest.urls.devicectl", "devicectl_api"), namespace="devicectl_api"),
    ),
    path(
        "autocomplete/pdb/ix",
        django_devicectl.autocomplete.views.peeringdb_ix.as_view(),
        name="pdb ix autocomplete",
    ),
    path(
        "autocomplete/pdb/org",
        django_devicectl.autocomplete.views.peeringdb_org.as_view(),
        name="pdb org autocomplete",
    ),
    path(
        "login/",
        auth_views.LoginView.as_view(template_name="devicectl/auth/login.html"),
        name="login",
    ),
    path("logout/", auth_views.LogoutView.as_view(next_page="/login"), name="logout"),
    path("<str:org_tag>/", views.view_instance, name="devicectl-home"),
    path(
        "apidocs/swagger",
        TemplateView.as_view(template_name="devicectl/apidocs/swagger.html",),
        name="swagger",
    ),
    path(
        "apidocs/redoc",
        TemplateView.as_view(template_name="devicectl/apidocs/redoc.html",),
        name="redoc",
    ),
    path("", views.org_redirect),
]
