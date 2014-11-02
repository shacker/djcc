from tastypie.resources import ModelResource
from courses.models import Course

class CourseResource(ModelResource):
    class Meta:
        queryset = Course.objects.all()
        allowed_methods = ['get']
