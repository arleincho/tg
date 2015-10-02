from django.contrib.auth import authenticate, login, logout as django_logout
# from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.shortcuts import render
from django.views.decorators.csrf import csrf_protect

from django.conf import settings
from django.core.urlresolvers import reverse

from twython import Twython
# from utils import AhorrandoRequest
from tasks.tasks import store_tweet
from tasks.tasks import store_post_ahorrando
from twitter.forms import Tweets

User = get_user_model()

# If you've got your own Profile setup, see the note in the models file
# about adapting this to your own setup.
from twitter.models import TwitterProfile


def logout(request, redirect_url=settings.LOGOUT_REDIRECT_URL):
    """
        Nothing hilariously hidden here, logs a user out. Strip this out if your
        application already has hooks to handle this.
    """
    django_logout(request)
    return HttpResponseRedirect(request.build_absolute_uri(redirect_url))


def begin_auth(request):
    """The view function that initiates the entire handshake.

    For the most part, this is 100% drag and drop.
    """
    # Instantiate Twython with the first leg of our trip.
    twitter = Twython(settings.TWITTER_KEY, settings.TWITTER_SECRET)

    # Request an authorization url to send the user to...
    callback_url = request.build_absolute_uri(reverse('twitter.views.thanks'))
    auth_props = twitter.get_authentication_tokens(callback_url)

    # Then send them over there, durh.
    request.session['request_token'] = auth_props
    return HttpResponseRedirect(auth_props['auth_url'])


def thanks(request, redirect_url='user_timeline'):

    """A user gets redirected here after hitting Twitter and authorizing your app to use their data.

    This is the view that stores the tokens you want
    for querying data. Pay attention to this.

    """
    # Now that we've got the magic tokens back from Twitter, we need to exchange
    # for permanent ones and store them...
    oauth_token = request.session['request_token']['oauth_token']
    oauth_token_secret = request.session['request_token']['oauth_token_secret']
    twitter = Twython(settings.TWITTER_KEY, settings.TWITTER_SECRET,
                      oauth_token, oauth_token_secret)

    # Retrieve the tokens we want...
    authorized_tokens = twitter.get_authorized_tokens(request.GET['oauth_verifier'])

    # If they already exist, grab them, login and redirect to a page displaying stuff.
    try:
        user = User.objects.get(username=authorized_tokens['screen_name'])
        try:
            user_twitter_profile = TwitterProfile.objects.get(user=user)
        except TwitterProfile.DoesNotExist:
            profile = TwitterProfile()
            profile.user = user
            profile.oauth_token = authorized_tokens['oauth_token']
            profile.oauth_secret = authorized_tokens['oauth_token_secret']
            profile.save()
    except User.DoesNotExist:
        # We mock a creation here; no email, password is just the token, etc.
        user = User.objects.create_user(authorized_tokens['screen_name'], "fjdsfn" + authorized_tokens['screen_name'] + ".com", authorized_tokens['oauth_token_secret'])
        profile = TwitterProfile()
        profile.user = user
        profile.oauth_token = authorized_tokens['oauth_token']
        profile.oauth_secret = authorized_tokens['oauth_token_secret']
        profile.save()

    user = authenticate(
        username=authorized_tokens['screen_name'],
        password=authorized_tokens['oauth_token_secret']
    )
    # login(request, user)
    request.session['twitterprofile'] = user
    return HttpResponseRedirect(redirect_url)

@csrf_protect
def user_timeline(request):
    """An example view with Twython/OAuth hooks/calls to fetch data about the user in question."""
    # user = request.user.twitterprofile
    tweets = {}
    if 'twitterprofile' in request.session:
        params = {'include_rts': False, 'count': 50}
        if 'max_id' in request.GET:
            params['max_id'] = request.GET['max_id']
        user = request.session['twitterprofile'].twitterprofile
        twitter = Twython(settings.TWITTER_KEY, settings.TWITTER_SECRET,
                          user.oauth_token, user.oauth_secret)
        user_tweets = twitter.get_user_timeline(**params)

        for tweet in user_tweets:
            tweets.update({tweet['id']: tweet['text']})
        try:
            newer = user_tweets[0]['id']
            older = user_tweets[-1]['id']
        except Exception:
            newer = False
            older = False

        # if request.method == 'POST':
        #     form = Tweets(tweets, request.POST)
        #     if 'token_ahorrando' not in request.session:
        #         r = AhorrandoRequest()
        #         r.login(request)
        #     if form.is_valid():
        #         tweets_form = form.save()
        #         for tweet_form in tweets_form:
        #             store_tweet.delay(tweet_form, tweets[int(tweet_form)])
        #             store_post_ahorrando.delay(tweet_form, tweets[int(tweet_form)], 'twitter', request.session['token_ahorrando']['token'])

        form = Tweets(tweets)
        return render(request, 'tweets.html', {'form': form, 'older': older, 'newer': newer})
    return HttpResponseRedirect(reverse_lazy('twitter_login'))
