# -*- coding: utf-8 -*-

from celery import task
from facebook.models import PostsTrace
from facebook.models import TokenPage
from facebook.models import ActionsFacebook
from twitter.models import TweetsTrace
# from utils import AhorrandoRequest
from django.db import IntegrityError
from django.core.exceptions import ObjectDoesNotExist
from open_facebook import OpenFacebook
from django.conf import settings
from twython import Twython
from django.contrib.auth import get_user_model

User = get_user_model()


# r = AhorrandoRequest()

@task(ignore_result=True)
def store_post(facebook_id, title):
    try:
        PostsTrace.objects.create(facebook_id=facebook_id, title=title)
    except IntegrityError as e:
        return {'facebook_id': facebook_id, 'duplicate key': facebook_id}


@task(ignore_result=True)
def store_tweet(twitter_id, title):
    try:
        TweetsTrace.objects.create(twitter_id=twitter_id, title=title)
    except IntegrityError as e:
        return {'twitter_id': twitter_id, 'duplicate key': twitter_id}



@task(ignore_result=True)
def store_post_ahorrando(facebook_id, title, network, token):
    return True
#     r.do_post({'facebook_id': facebook_id, 'content': title, 'network': network}, token)



@task(ignore_result=True)
def sum_points_ahorrando(post_id, user_facebook_id, token, action, points, network):
    return True
#     r.do_post({'post': post_id, 'user': user_facebook_id, 'network': network, 'action': action, 'points': points}, token, '/points/')



@task(ignore_result=True)
def search_likes():
    call_api_facebook.delay(path='/likes', fields="id", action='like', points=5)


@task(ignore_result=True)
def search_comments():
    call_api_facebook.delay(path='/comments', fields="id,from", action='comment', points=10)



@task(ignore_result=True)
def search_shares():
    call_api_facebook.delay(path='/sharedposts', fields="id,from", action='shared', points=15)


@task(ignore_result=True)
def call_api_facebook(path, fields, action, points):
    try:
        # token_facebook = TokenPage.objects.get(provider='facebook')
        token_facebook = 'CAADlZAjddyj4BADinoGOsEZC5J5V3icTeX57Q9ELhffwxaHth9w3CHZAb9JO6XFZAutu6ZCRwhrsPgVZAnMzjZA5O8ZABDamW7IbnJyEA3KCGvkTjjb4CDTonh0X2JZBKvxR4DAO362WxTUeIfkfYLdiRicTnf1lRX74UzeXN8GI4dpkErsJ8DH1W'
        token_ahorrando = TokenPage.objects.get(provider='ahorrando')
        posts = PostsTrace.objects.all().values('facebook_id')
        # graph = OpenFacebook(token_facebook.token)
        graph = OpenFacebook(token_facebook)
        count = 1
        data = {'fields': fields}
        for post in posts:
            more_items = True
            while more_items:
                count += 1
                fb_objects = graph.get("%s%s" % (post['facebook_id'], path), **data)
                if 'paging' in fb_objects:
                    if 'limit' in data:
                        del data['limit']
                    if 'after' in data:
                        del data['after']
                    if  'next' not in fb_objects['paging']:
                        more_items = False
                    else:
                        data['limit'] = 25
                        data['after'] = fb_objects['paging']['cursors']['after']

                for fb_object in fb_objects['data']:
                    facebook_user_id = fb_object['from']['id'] if 'from' in fb_object else fb_object['id']
                    count = ActionsFacebook.objects.filter(post_id=post['facebook_id'], facebook_user_id=facebook_user_id, action=action).count()
                    if count < 1:
                        try:
                            ActionsFacebook.objects.create(post_id=post['facebook_id'], facebook_user_id=facebook_user_id, action=action)
                            sum_points_ahorrando.delay(post['facebook_id'], facebook_user_id, token_ahorrando, action, points, 'facebook')
                        except IntegrityError:
                            pass
                if not more_items:
                    break
    except ObjectDoesNotExist:
        print("Either the entry or blog doesn't exist.")


@task(ignore_result=True)
def search_retweets():
    try:
        token_twitter = User.objects.get(username=settings.TWITTER_ACCOUNT).twitterprofile
        twitter = Twython(settings.TWITTER_KEY, settings.TWITTER_SECRET,
                          token_twitter.oauth_token, token_twitter.oauth_secret)
        token_ahorrando = TokenPage.objects.get(provider='ahorrando')
        tweets = TweetsTrace.objects.all().values('twitter_id')
        data = {}
        for tweet in tweets:
            more_items = True
            data = {'id': tweet['twitter_id']}
            while more_items:
                retweets = twitter.get_retweeters_ids(**data)

                if 'next_cursor' in retweets:
                    if retweets['next_cursor'] == 0:
                        more_items = False
                    else:
                        data['cursor'] = retweets['next_cursor']

                if 'ids' in retweets:
                    for user in retweets['ids']:
                        count = ActionsFacebook.objects.filter(post_id=tweet['twitter_id'], facebook_user_id=user, action='retweet').count()                    
                        if count < 1:
                            try:
                                ActionsFacebook.objects.create(post_id=tweet['twitter_id'], facebook_user_id=user, action='retweet')
                                sum_points_ahorrando.delay(tweet['twitter_id'], user, token_ahorrando, 'retweet', 15, 'twitter')
                            except IntegrityError:
                                pass

                if not more_items:
                    break
    except ObjectDoesNotExist:
        print("Either the entry or blog doesn't exist.")
