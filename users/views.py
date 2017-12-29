# -*- coding: utf-8 -*-
import time
from django.urls import reverse
from django.conf import settings
from common import http, router,\
    loginRequired, permRequired, \
    OKResponse

def _clean_session(pk, call_back=None):
    """
    clean single session, pk is the session key 
    """
    from django.contrib.sessions.models import Session
    s = Session.objects.filter(session_key = pk)
    data = s.get().get_decoded()
    if call_back:
        call_back(data)
    s.delete()

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

@router(r"^(?i)/login$", method=["GET"])
def login(request):
    ip = get_client_ip(request)
    request.session[settings.LOGIN_KEY] = ip
    request.session["username"] = ip
    request.session[settings.PERM_TABLE_NAME] = {}
    return http.HttpResponseRedirect(reverse("Index"))


@router(r"^(?i)/logout$")
def logout(request):
    sk = request.session.session_key
    if sk:
        _clean_session(sk)
        request.session.flush()
    response = http.JsonResponse(
        {"err_code": 0, "data": None}
        )
    response.set_cookie(key=settings.SESSION_COOKIE_NAME, 
                        value=sk,
                        expires=0)
    return response


@router(r"^(?i)/index$", loginRequired=True)
class Index(http.ViewBase):

    def get(self, request):
        username = request.session["username"]
        timepoint = time.strftime("%Y-%m-%d %H:%M:%S", 
            time.localtime(time.time()))
        data = "user %s visit this page at %s" % (username, timepoint)
        return OKResponse(data)

    @permRequired("sudo")
    def post(self, request):
        return OKResponse("NB! sudoer!")


@router(r"^(?i)/detail$", permRequired="sudo")
class Detail(http.ViewBase):

    def get(self, request):
        username = request.session["username"]
        return OKResponse(username)


