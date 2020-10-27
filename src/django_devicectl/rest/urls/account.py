from django.urls import path, include

import django_devicectl.rest.views.account
import django_devicectl.rest.route.account

urlpatterns = [
    path("", include(django_devicectl.rest.route.account.router.urls)),
]
