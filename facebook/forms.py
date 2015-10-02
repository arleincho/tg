from django import forms



class PostFacebook(forms.Form):

    posts_facebook = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple)

    def __init__(self, posts, *args, **kwargs):
        super(PostFacebook, self).__init__(*args, **kwargs)
        self.fields['posts_facebook'] = forms.MultipleChoiceField(choices=[(k, posts[k]) for k in posts],
            widget=forms.CheckboxSelectMultiple)


    def clean_posts_facebook(self):
        posts_facebook = self.cleaned_data.get("posts_facebook", None)
        self._posts_facebook = posts_facebook
        return self.cleaned_data

    def save(self):
        """
        Just return the authenticated user - used for sending login
        email.
        """
        return getattr(self, "_posts_facebook", None)
