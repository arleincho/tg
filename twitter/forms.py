from django import forms



class Tweets(forms.Form):

    tweets = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple)

    def __init__(self, posts, *args, **kwargs):
        super(Tweets, self).__init__(*args, **kwargs)
        self.fields['tweets'] = forms.MultipleChoiceField(choices=[(k, posts[k]) for k in posts],
            widget=forms.CheckboxSelectMultiple)


    def clean_tweets(self):
        tweets = self.cleaned_data.get("tweets", None)
        self._tweets = tweets
        return self.cleaned_data

    def save(self):
        """
        Just return the authenticated user - used for sending login
        email.
        """
        return getattr(self, "_tweets", None)
