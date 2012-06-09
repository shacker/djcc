"""
Assign students to random majors. Dev use only!!! Not to be run on production!
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
from courses.models import Course,Offering,Program


setup_environ(settings)

#################### Start work

offerings = Offering.objects.all()
for o in offerings:
    c = Course.objects.get(ccn=o.ccn)
    print c
    o.course = c
    o.save()