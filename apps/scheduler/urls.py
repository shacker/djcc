from django.conf.urls.defaults import *
from scheduler import views

urlpatterns = patterns('scheduler.views',

    url(r'^$',
        'scheduler',
        name='scheduler'),

    url(r'^add/(?P<offering_id>[\d]+)$',
        'add_course_to_schedule',
        name='add_course_to_schedule'
        ),

    url(r'^remove/(?P<offering_id>[\d]+)$',
        'remove_course_from_schedule',
        name='remove_course_from_schedule'
        ),

)

