from django.urls import path, include
from django.contrib import admin

import fullctl.django.views as views
import django_devicectl.urls

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("social_django.urls", namespace="social")),
    path("", include("fullctl.django.urls")),
    path("", include("django_devicectl.urls")),
    path("", views.org_redirect),
]
