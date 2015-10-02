
# Register your models here.
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from facebook.models import PostsTrace
from facebook.models import ActionsFacebook




class PostsTraceAdmin(admin.ModelAdmin):

    list_display = ('facebook_id', 'title', 'datetime')
    search_fields = ('facebook_id',)



class ActionsFacebookAdmin(admin.ModelAdmin):

    list_display = ('post_id', 'facebook_user_id', 'action', 'datetime')
    search_fields = ('facebook_user_id', 'action')
    list_filter = ('action', 'post_id')




admin.site.register(PostsTrace, PostsTraceAdmin)
admin.site.register(ActionsFacebook, ActionsFacebookAdmin)
