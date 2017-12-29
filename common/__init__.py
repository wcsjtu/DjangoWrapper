# -*- coding: utf-8 -*-
from . import task
from .decorators import router, \
    loginRequired, permRequired
from . import err_code


OKResponse = lambda d: {"data": d, "err_code": err_code.OK}
