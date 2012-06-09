"""
This was a one-off to protect identity of people in initial data set - can prob be deleted.
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
from subgroups.models import Subgroup

setup_environ(settings)

#################### Start work

# Get random words for group names from nouns.txt - read all into memory once.
lines = file('scripts/nouns.txt').read().splitlines()
names = file('scripts/randomNames.csv').read().splitlines()




# Randomize all names
users = User.objects.all()
for u in users:
    line = names[randint(1, len(names))]
    nl = line.split(',')
    u.first_name = nl[0]
    u.last_name = nl[1]
    u.save()
