from django.conf.urls.defaults import *
from courses.models import *

# Program/courses URLs
urlpatterns = patterns('courses.views',
    
    url(r'^(?P<program_slug>[\w-]+)/$', 'program_detail', name="program_detail"),    

)
