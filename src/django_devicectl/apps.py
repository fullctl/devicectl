from django.apps import AppConfig


class DjangoDevicectlConfig(AppConfig):
    name = "django_devicectl"
    label = "django_devicectl"

    def ready(self):
        import django_devicectl.signals
