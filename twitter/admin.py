
# Register your models here.
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from twitter.models import TweetsTrace



class TweetsTraceAdmin(admin.ModelAdmin):

    list_display = ('twitter_id', 'title', 'datetime')
    search_fields = ('twitter_id',)


admin.site.register(TweetsTrace, TweetsTraceAdmin)
