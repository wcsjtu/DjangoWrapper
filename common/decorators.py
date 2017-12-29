# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals
from functools import wraps

from django.conf.urls import url, include
from django.conf import settings
from django.utils.module_loading import import_module
from django.http import HttpRequest
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator

from common import utils, http

router_map = getattr(settings, "ROUTER_FILES")
router_module = import_module(router_map)


def router(regex, **options):
    """
    修饰函数或者common.http.ViewBase的子类, 将regex映射到函数或者类
    @params:
      regex, 字符串, url映射的正则表达式
      options, 各种配置参数, 具体如下
        base, 字符串, 上一层url的正则表达式, 如base = r"^merge";
        method, 列表, 只有在修饰函数时生效, 表示哪些http方法会映射到这个函数, 如 method=["GET", "POST", "OPTION"];
        loginRequired, bool, 表示该url是否需要登录才能访问, 默认是不用登录;
        permRequired, 字符串, 表示该url是否需要某种权限才能访问, 如 permRequired = "configUser";
        csrf_exempt, bool, 表示是否校验该url post请求的csrf_cookie
    """
    def _router(func_or_cls):
        maps = getattr(router_module, "maps")
        base = options.pop("base", None)
        func_or_cls = _decorate(func_or_cls, options)
        func = _func(func_or_cls)
        name = _func_name(func_or_cls)
        item = url(regex, func, name=name)
        if base:
            item = url(base, include([item]))
        maps.append(item)
        setattr(router_module, "maps", maps)
        return func_or_cls
    return _router

def make_decorator(decorator, iscls, method_name="dispatch"):
    return method_decorator(decorator, name=method_name) \
        if iscls else decorator

def _func(func_or_cls):
    if isinstance(func_or_cls, type):
        func =  func_or_cls.as_view()
    else:
        func = func_or_cls
    return func

def _func_name(func_or_cls):
    return func_or_cls.__name__ if isinstance(func_or_cls, type) else func_or_cls.func_name

def _decorate(func_or_cls, options):
    flag = isinstance(func_or_cls, type)
    if options.get("method", []):
        func_or_cls = make_decorator(require_http_methods, flag)(options["method"])(func_or_cls)
    if options.get("loginRequired", False):
        func_or_cls = make_decorator(loginRequired, flag)(func_or_cls)
    if options.get("permRequired"):
        perm = options.get("permRequired")
        func_or_cls = make_decorator(permRequired(perm), flag)(func_or_cls)
    if options.get("csrf_exempt", False):
        func_or_cls = make_decorator(csrf_exempt, flag)(func_or_cls)
    return func_or_cls


def loginRequired(func_or_cls):
    @wraps(func_or_cls)
    def wrapper(*args, **kwargs):
        if isinstance(args[0], HttpRequest):    
            request = args[0]
        else:
            request = args[1]
        utils.checksession(request)
        return func_or_cls(*args, **kwargs)
    return wrapper


def permRequired(permType):
    def _permRequired(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if isinstance(args[0], HttpRequest):    
                request = args[0]
            else:
                request = args[1]
            utils.checksession(request)
            utils.checkUserPerm(request, permType)
            return func(*args, **kwargs)
        return wrapper
    return _permRequired

__all__ = ["router", "csrf_exempt"]