from tastypie.resources import ModelResource
from resources.models import Room

class RoomResource(ModelResource):
    class Meta:
        queryset = Room.objects.all()
        allowed_methods = ['get']
