
# from restkit import Resource
from django.db import IntegrityError
from facebook.models import TokenPage

try:
    import simplejson as json
except ImportError:
    import json

class AhorrandoRequest():

    def __init__(self, **kwargs):
        url = "https://www.ahorrandoahorrando.com/api/v1"
        # super(AhorrandoRequest, self).__init__(url, follow_redirect=False,
        #                                 max_follow_redirect=0, **kwargs)

    def login(self, request):
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        payload = "username=admin&password=W7cY{wj(4~]@rsdfasJHKJi"
        resp = super(AhorrandoRequest, self).post(path="/token/", payload=payload, headers=headers)
        request.session['token_ahorrando'] = json.loads(resp.body_string())
        try:
            TokenPage.objects.filter(provider='ahorrando').delete()
            TokenPage.objects.create(token=request.session['token_ahorrando']['token'], provider='ahorrando')
        except IntegrityError:
            pass

    def do_post(self, data={}, token='', path="/blog/"):
        headers = {"Authorization": "Token %s" % token}
        resp = super(AhorrandoRequest, self).post(path=path, payload=data, headers=headers)
        print(resp.body_string())