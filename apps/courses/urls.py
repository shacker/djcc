from django.conf.urls.defaults import *
from courses.models import *

# Program/courses URLs
urlpatterns = patterns('courses.views',

    # Course schedule and its printable version all use the same view, and can optionally take a "sem" (semester) argument.
    url(r'^schedule/sem/(?P<sem_id>[\d]+)/$', 'offerings_schedule', name="courses_schedule_sem"),
    url(r'^descriptions/sem/(?P<sem_id>[\d]+)/$', 'offerings_schedule', {'printable': True}, name="courses_descriptions_sem"),
    url(r'^schedule/$', 'offerings_schedule', name="offerings_schedule"),
    url(r'^descriptions/$', 'offerings_schedule', {'printable': True}, name="courses_descriptions"),
    url(r'^categories/$', 'program_categories', name="program_categories"),
    url(r'^majors/$', 'program_majors', name="program_majors"),

    url(r'^category/(?P<slug>[\w-]+)/$', 'program_category', name='program_category'),
    url(r'^major/(?P<slug>[\w-]+)/$', 'program_major', name='program_major'),

    url(r'^class/(?P<course_id>[\d]+)$', 'offering_detail', name="offering_detail"),
    url(r'^class/(?P<course_id>[\d]+)/schedule$', 'offering_schedule', name="offering_schedule"),
    url(r'^class/(?P<course_id>[\d]+)/announcements$', 'offering_announcements', name="offering_announcements"),
    url(r'^class/(?P<course_id>[\d]+)/contact$', 'offering_contact', name="offering_contact"),
    url(r'^class/(?P<course_id>[\d]+)/policies$', 'offering_policies', name="offering_policies"),    
    url(r'^class/(?P<course_id>[\d]+)/assignments$', 'offering_assignments', name="offering_assignments"),        
    url(r'^class/(?P<course_id>[\d]+)/participants$', 'offering_participants', name="offering_participants"),            
    url(r'^class/(?P<course_id>[\d]+)/materials$', 'offering_materials', name="offering_materials"),            
    url(r'^class/(?P<course_id>[\d]+)/library$', 'offering_library', name="offering_library"),                
    url(r'^class/(?P<course_id>[\d]+)/public$', 'offering_public', name="offering_public"),                

    url(r'^material/(?P<material_id>[\d]+)$', 'offering_material_detail', name="offering_material_detail"),            
    url(r'^assignment/(?P<assign_id>[\d]+)$', 'offering_assignment_detail', name="offering_assignment_detail"),            
)

