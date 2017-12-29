# -*- coding: utf-8 -*-

from __future__ import absolute_import
from functools import wraps

from django import http
from django.http import *
from django.template.loader import render_to_string
from django.shortcuts import render, render_to_response
from django.views.generic import base
from django.core.exceptions import PermissionDenied, DisallowedHost, \
    DisallowedRedirect, TooManyFieldsSent, \
    RequestDataTooBig

from django.urls import reverse

def _load_errno():
    import json
    from . import err_code
    from django.conf import settings
    errno_file = settings.ERRNO_FILE
    with open(errno_file, "r") as f:
        d = json.load(f)
    code, tips = d
    for key, val in code.items():
        setattr(err_code, key.upper(), val)
    tips = {int(k):v for k, v in tips.items()}
    setattr(err_code, "TIPS", tips)
    return tips

class LowerCaseMethod(type):

    def __new__(cls, name, bases, attrs):

        methods = bases[0].http_method_names

        for key in attrs.keys():
            if key.lower() in methods:
                attrs[key.lower()] = attrs.pop(key)
        return super(LowerCaseMethod, cls).__new__(cls, name, bases, attrs)


class ViewBase(base.View):
    __metaclass__ = LowerCaseMethod

    @property
    def cls(self):
        #clsname = self.__class__.__name__
        #return reverse(clsname)            # 有没有需要加?
        return self.__class__.__name__


class NotAllowedMethod(Exception):pass


class ErrorResp(Exception):

    TIPS = _load_errno()

    def __init__(self, err_no, tips=None):
        self.errno = err_no
        if not tips:
            tips = self.TIPS.get(err_no, 
                             "unknown error with code %d" % err_no)
        super(ErrorResp, self).__init__(tips)

    def __iter__(self):
        return iter([("err_code", self.errno), ("data", None)])
        



__all__ = http.__all__ + ["render", "ErrorResp",
                          "render_to_response",
                          "render_to_string",
                          "ViewBase", 
                          "NotAllowedMethod",
                          ] + [
                          "PermissionDenied", 
                          "DisallowedHost", 
                          "DisallowedRedirect", 
                          "TooManyFieldsSent", 
                          "RequestDataTooBig"
                          ]