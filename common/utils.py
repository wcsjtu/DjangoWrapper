# -*- coding: utf-8 -*-
from __future__ import absolute_import
from django.conf import settings
from common import err_code
from common import http 

def checksession(request):
    """
    @params:
        request, django请求实例
    @function:
        判断是否已经登录
    """
    if not settings.LOGIN_KEY in request.session:        
        raise http.ErrorResp(err_code.NO_LOGIN)
    return err_code.OK

def checkUserPerm(request, permType):
    """
    @params:
        reqeuest, HttpRequest实例
        permType, 权限类型
    @function:
        检查用户是否有权限进入该页面
    """
    name = settings.PERM_TABLE_NAME
    if not request.session[name].get(permType, 0):
        raise http.ErrorResp(err_code.NO_PERM)
    return err_code.OK

