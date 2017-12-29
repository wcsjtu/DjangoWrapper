"""
WSGI config for  project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/howto/deployment/wsgi/
"""

import os
import sys, logging
from os.path import join,dirname,abspath
 
from django.core.wsgi import get_wsgi_application
from django.conf import settings

from .__init__ import PROJECT_NAME

os.environ.setdefault("DJANGO_SETTINGS_MODULE", PROJECT_NAME + ".settings")

enable = getattr(settings, "ENABLE_WEBSOCKET", False)

_django_app = get_wsgi_application()
if enable:
    from ws4redis.uwsgi_runserver import uWSGIWebsocketServer
    _websocket_app = uWSGIWebsocketServer()
else:
    logger = logging.getLogger("django.request")
    _websocket_app = _django_app
    logger.warn("websocket support is disabled!!!")

def application(environ, start_response):
    if environ.get('PATH_INFO').startswith(settings.WEBSOCKET_URL): #if uri like /ws/****, then redirect to websocket app
        return _websocket_app(environ, start_response)
    return _django_app(environ, start_response)