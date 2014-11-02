from tastypie.resources import ModelResource
from news.models import Story

class StoryResource(ModelResource):
    class Meta:
        queryset = Story.objects.all()
        allowed_methods = ['get']
