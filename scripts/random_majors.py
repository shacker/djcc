"""
Create initial users and groups
"""

#################### Set up Django environment
import sys,os
from random import randint


# For dev use :
sys.path.append('.')
sys.path.append('../')
sys.path.append('../lib/python2.7/site-packages/django')

# For production use:
# sys.path.append('/home/shacker/lib/python2.7')
# sys.path.append('/home/shacker/webapps/django')
# sys.path.append('/home/shacker/webapps/django/bucketlist')
# sys.path.append('/home/shacker/webapps/django/lib/python2.7/django')


os.environ['DJANGO_SETTINGS_MODULE'] ='djcc.settings'

from django.core.management import setup_environ
from djcc import settings
from django.contrib.auth.models import User, Group
from courses.models import Course, Major

setup_environ(settings)

#################### Start work

courses = Course.objects.all()
for c in courses:
    major = Major.objects.order_by('?')[:1].get()
    c.majors.add(major)
    