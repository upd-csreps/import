"""
ASGI config for import project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application
from .websocket import websocket_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'import.settings')

django_application = get_asgi_application()

async def application(scope, receive, send):
    if scope['type'] == 'http':
        # Let Django handle HTTP requests
        await django_application(scope, receive, send)
    elif scope['type'] == 'websocket':
        # We'll handle Websocket connections here
        await websocket_application(scope, receive, send)
    else:
        raise NotImplementedError(f"Unknown scope type {scope['type']}")