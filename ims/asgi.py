"""
ASGI config for ims project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/howto/deployment/asgi/
"""

import os

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ims.settings')
django.setup()

from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
import src.notification.urls

django_asgi_app = get_asgi_application()
application = ProtocolTypeRouter({
    "http": django_asgi_app,
    # Only allow socket connections from the Allowed hosts in the settings.py file
    'websocket': URLRouter(
        # [
        src.notification.urls.websocket_urlpatterns1
        # ]
    )

})
