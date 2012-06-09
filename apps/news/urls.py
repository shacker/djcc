from django.conf.urls.defaults import *
from news import views

urlpatterns = patterns('',
    url(r'^$', 
        views.story_list,
        name='news_story_list'),
        
    url(r'^(?P<story_id>\d+)$', 
        views.story_detail,
        name='news_story_detail'),        
)

