
from django.conf import settings
from django.shortcuts import render
from django.http import HttpResponse
from django_facebook.decorators import facebook_required, facebook_required_lazy
from django_facebook.api import get_persistent_graph, get_facebook_graph
from django.views.decorators.csrf import csrf_protect
from django.shortcuts import redirect
from django.core.urlresolvers import reverse
from django.shortcuts import render
from facebook.forms import PostFacebook
from facebook.models import TokenPage
from open_facebook import OpenFacebook
from app.utils import AhorrandoRequest
from tasks.tasks import store_post
from tasks.tasks import store_post_ahorrando
from django.db import IntegrityError
from urllib.parse import urlparse

page_id = getattr(settings, 'FACEBOOK_PAGE_ID', None)

@facebook_required(scope='manage_pages,read_stream')
@csrf_protect
def read_posts(request):
    fb = get_facebook_graph(request)
    pages = fb.get('me/accounts')
    if 'data' in pages:
        for page in pages['data']:
            if page_id is not None and page['id'] == page_id:
                request.session['access_token_page'] = page['access_token']
                TokenPage.objects.filter(provider='facebook').delete()
                TokenPage.objects.create(token=page['access_token'], provider='facebook')
    return redirect(reverse('get_posts'))



# @facebook_required(scope='manage_pages')
@csrf_protect
def get_posts(request):
    posts_form = {}
    context = {}
    request.session['access_token_page'] = 'CAADlZAjddyj4BADinoGOsEZC5J5V3icTeX57Q9ELhffwxaHth9w3CHZAb9JO6XFZAutu6ZCRwhrsPgVZAnMzjZA5O8ZABDamW7IbnJyEA3KCGvkTjjb4CDTonh0X2JZBKvxR4DAO362WxTUeIfkfYLdiRicTnf1lRX74UzeXN8GI4dpkErsJ8DH1W'
    if 'access_token_page' in request.session:
        graph = OpenFacebook(request.session['access_token_page'])
        params_qs = {}
        if request.method == "GET":
            if 'limit' in request.GET:
                params_qs['limit'] = request.GET['limit']
            if 'since' in request.GET:
                params_qs['since'] = request.GET['since']
                context['since'] = params_qs['since'] 
            if 'until' in request.GET:
                params_qs['until'] = request.GET['until']
                context['until'] = params_qs['until']

        if request.method == "POST":
            if 'limit' in request.POST:
                params_qs['limit'] = request.POST['limit']
            if 'until' in request.POST:
                params_qs['until'] = request.POST['until']
                context['until'] = params_qs['until']
            if 'since' in request.POST:
                params_qs['since'] = request.POST['since']
                context['since'] = params_qs['since']

        params_qs['fields'] = 'object_id,message,from,story'
        context['limit'] = params_qs['limit'] if 'limi' in params_qs else 25


        posts = graph.get("%s%s" % (page_id, '/feed'), **params_qs)
        if 'paging' in posts:
            if 'next' in posts['paging']:
                context['next'] = urlparse(posts['paging']['next']).query
            if 'previous' in posts['paging']:
                context['previous'] = urlparse(posts['paging']['previous']).query

        for post in posts['data']:
            if 'from' in post:
                object_id = post['id']
                if 'object_id' in post and post['from']['id'] == page_id:
                    object_id = post['object_id']
                if 'message' in post:
                    posts_form.update({object_id.replace(page_id + "_", ""): post["message"]})
        if request.method == "POST":
            form = PostFacebook(posts_form, request.POST)
            # if 'token_ahorrando' not in request.session:
            #     r = AhorrandoRequest()
            #     r.login(request)
            if form.is_valid():
                posts = form.save()
                for post in posts:
                    store_post.delay(post, posts_form[post])
                    # store_post_ahorrando.delay(post, posts_form[post], 'facebook', request.session['token_ahorrando']['token'])
                    # store_post_ahorrando.delay(post, posts_form[post], '8b045701b3daacb380acc4341eb961b0ef7143cf')
    form = PostFacebook(posts_form)
    context['form'] = form
    return render(request, 'index.html', context)


    