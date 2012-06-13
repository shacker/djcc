from tastypie.resources import ModelResource
from tastypie import fields
from courses.models import Course, Offering
from people.models import Profile
from resources.models import Room


class RoomsResource(ModelResource):
    class Meta:
        queryset = Room.objects.all()
        resource_name = 'location'

class CourseResource(ModelResource):
    class Meta:
        queryset = Course.objects.all()
        resource_name = 'course'


class OfferingsResource(ModelResource):
	location = fields.ForeignKey(RoomsResource, 'location',full=True)
	course = fields.ForeignKey(CourseResource, 'course',full=True)

	class Meta:
		queryset = Offering.objects.all()
		resource_name = 'course_offerings'


class PeopleResource(ModelResource):
    class Meta:
        queryset = Profile.active_objects.all()
        resource_name = 'people'