

from django.conf import settings
from django.db import models
# from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _




class TwitterProfile(models.Model):
    """
        An example Profile model that handles storing the oauth_token and
        oauth_secret in relation to a user. Adapt this if you have a current
        setup, there's really nothing special going on here.
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL)
    oauth_token = models.CharField(max_length=200)
    oauth_secret = models.CharField(max_length=200)


class TweetsTrace(models.Model):
    twitter_id = models.BigIntegerField(unique=True, blank=False, null=False)
    title = models.CharField(_('title'), blank=False, null=False, max_length=200)
    datetime = models.DateTimeField('date published', auto_now_add=True)


