from django.contrib.syndication.views import Feed, FeedDoesNotExist
from django.core.exceptions import ObjectDoesNotExist
from news.models import Story
import datetime, time
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse


class LatestNews(Feed):
    title = "CalCentral: Recently news"
    link = "http://example.com"    
    description = "Latest news on CalCentral"
    
    title_template = 'feeds/news_title.html'
    description_template = 'feeds/news_description.html'

    def items(self):
        items = list(Story.objects.all().order_by('-pubdate')[:10])
        return items

    def item_link(self,obj):
        return reverse('news_story_detail',args=[obj.id])