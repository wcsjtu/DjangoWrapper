# -*- coding: utf-8 -*-

from django.utils.deprecation import MiddlewareMixin
from django import http
from common.http import ErrorResp

class Format(MiddlewareMixin):

    def process_response(self, request, response):
        ret = response
        if type(ret) in [str, unicode, int, bool]:
            ret = http.HttpResponse(ret)
        elif type(ret) is dict:
            ret = http.JsonResponse(ret)
        elif hasattr(ret, "__iter__") and not isinstance(ret, http.response.HttpResponseBase):
            ret = http.StreamingHttpResponse(ret)
            ret["Content-Type"] = "application/octet-stream" 
        return ret

    def process_exception(self, request, exception):        
        if isinstance(exception, ErrorResp):
            return dict(exception)
        else:
            return None