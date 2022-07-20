from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver


@receiver(user_logged_in)
def handle_login(sender, **kwargs):
    user = kwargs.get("user")
