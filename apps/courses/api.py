from tastypie.resources import ModelResource
from courses.models import Offering


class OfferingsResource(ModelResource):
    class Meta:
        queryset = Offering.objects.all()
        resource_name = 'offerings'