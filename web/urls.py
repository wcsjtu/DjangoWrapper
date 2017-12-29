""" URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
import os
import logging
from django.conf.urls import url, include
from django.contrib import admin
from django.conf import settings


def load_app():
    folders = os.listdir(".")
    apps = settings.INSTALLED_APPS
    ret = []
    for f in folders:
        if os.path.isdir(f) and f in apps:
            ret.append(f)
    return ret


def import_view():
    from django.utils.module_loading import import_module
    urlpatterns = []
    router_map = settings.ROUTER_FILES
    backend_prefix = settings.BACKEND_URL_PREFIX
    router_module = import_module(router_map)
    for app in load_app():
        module = import_module("%s.views" % app)
        maps = getattr(router_module, "maps")
        prefix = r"^%s/%s" % (backend_prefix, app)
        if not maps:
            module = import_module("%s.urls" % app)
            maps = getattr(module, "urlpatterns")
            if not maps:
                logging.warn("load App %s failed!" % app)
            else:
                urlpatterns += [url(prefix, include(maps))]
            continue
        urlpatterns += [url(prefix, include(maps))]
        setattr(router_module, "maps", [])
    return urlpatterns

urlpatterns = import_view()

if settings.DEBUG:
    def default(request):
        with open(settings.INDEX_HTML_PATH, "r") as f:
            data = f.read()
        return data
    u = url(r"^(?!%s).+" % settings.BACKEND_URL_PREFIX, default )
    urlpatterns.insert(0, u)