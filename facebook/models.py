
from django.db import models
from django.utils.translation import ugettext_lazy as _



class PostsTrace(models.Model):
    facebook_id = models.BigIntegerField(unique=True, blank=False, null=False)
    title = models.CharField(_('title'), blank=False, null=False, max_length=200)
    datetime = models.DateTimeField('date published', auto_now_add=True)



PROVIDER = (
    ('facebook', 'Facebook'),
    ('ahorrando', 'Ahorrando'),
    ('twitter', 'Twitter'),
)

ACTIONS = (
    ('shared', 'Shared'),
    ('comment', 'Comment'),
    ('like', 'Like'),
    ('retweet', 'Retweet'),
    ('tweet', 'Tweet'),
)


class TokenPage(models.Model):

    token = models.CharField(unique=True, blank=False, null=False, max_length=400)
    provider = models.CharField(_('provider'), max_length=10, blank=False, null=False, choices=PROVIDER)
    datetime = models.DateTimeField('date published', auto_now_add=True)


class ActionsFacebook(models.Model):

    post_id = models.BigIntegerField(blank=False, null=False)
    facebook_user_id = models.BigIntegerField(blank=False, null=False)
    action = models.CharField(choices=ACTIONS, blank=False, null=False, max_length=10)
    datetime = models.DateTimeField('date published', auto_now_add=True)

    class Meta:
        unique_together = (("post_id", "facebook_user_id", "action"),)

