# -*- coduing: utf-8 -*-
from __future__ import absolute_import 
import os
import logging
from django.conf import settings
from django.utils.module_loading import import_module, import_string


PROJECT_NAME = os.path.split(os.path.dirname(__file__))[-1]

logger = logging.getLogger("django.request")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", PROJECT_NAME + ".settings")


asyn_tasks_modules = getattr(settings, "CELERY_ASYN_TASKS", None)
enable = getattr(settings, "ENABLE_CELERY", False)


def register_dill():
    from dill import dill
    from kombu.serialization import pickle_loads, pickle_protocol, registry
    from kombu.utils.encoding import str_to_bytes

    def encode(obj, dumper=dill.dumps):
        return dumper(obj, protocol=pickle_protocol)

    def decode(s):
        return pickle_loads(str_to_bytes(s), load=dill.load)

    registry.register(
        name='dill',
        encoder=encode,
        decoder=decode,
        content_type='application/x-python-serialize',
        content_encoding='binary'
    )


class Wrapper(object):

    def __getattr__(self, key):
        raise AttributeError(
                "you try to access an attribute in celery, "
                "but celery function(asynchronous task) is disabled!"
                "set `ENABLE_CELERY` as True to enable it"
                )
        
app = Wrapper()
task = Wrapper()

if asyn_tasks_modules and enable:
    from celery import Celery, task
    register_dill()
    app = Celery(settings.PROJECT_NAME)
    app.config_from_object("django.conf:settings")
    app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
    for asyn_tasks_module in asyn_tasks_modules:
        module = import_module(asyn_tasks_module)
        funcs = import_string(asyn_tasks_module + ".tasks")
        for func_name in funcs:
            func = getattr(module, func_name)
            new_func = task(func)
            doc_string = getattr(func, "func_doc", "")
            setattr(new_func, "func_doc", doc_string)
            setattr(module, func_name, new_func)
        setattr(module, "app", app)
elif asyn_tasks_modules:
    for asyn_tasks_module in asyn_tasks_modules:
        module = import_module(asyn_tasks_module)
        setattr(module, "app", app)
    logger.warn("you seem to use asynchronous function in django, but that function"
                " is disabled yet, please set `ENABLE_CELERY` as True!!!")
elif enable:
    logger.info("celery is enabled, make sure celery process is running! "
                "no registered task yet!")


