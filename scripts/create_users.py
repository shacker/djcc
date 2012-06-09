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
from subgroups.models import Subgroup

setup_environ(settings)

#################### Start work

# Get random words for group names from nouns.txt - read all into memory once.
lines = file('scripts/nouns.txt').read().splitlines()
names = file('scripts/randomNames.csv').read().splitlines()


# Create 100(?) subgroups
for g in range(1,100):
    try:
        groupname = lines[randint(1, len(lines))]
        Subgroup.objects.create(name="%s" % groupname)
        print "Created group %s" % groupname        
    except:
        print "Could not create group %s" % groupname
        

# Create 25 "testNN" student users
g = Group.objects.get(name='students') 
for u in range(1,26):
    try:
        username = "test%s" % str(u)
        user = User.objects.create_user(username, 'user@example.com', 'testuser')
        user.first_name = "Test"
        user.last_name = "User %s" % str(u)
        g.user_set.add(user) # Add this student to the "Students" group        
        user.save()
    except:
        print "Could not create user %s" % u


# Create a ton of randomly named student users
# Add all to Group "students" and to at least one randomly selected Subgroup
g = Group.objects.get(name='students')
for u in range(1,5000):
    try:
        line = names[randint(1, len(names))]
        nl = line.split(',')
        username = "%s.%s" % (nl[0],nl[1])
        user = User.objects.create_user(username.lower(), 'user@example.com', 'testuser')
        user.first_name = nl[0]
        user.last_name = nl[1]
        g.user_set.add(user) # Add this student to the "Students" group

        # Add user to a random subgroup (big query action here unfortunately)
        s = Subgroup.objects.order_by('?')[:1].get()
        s.members.add(user) # Add this student to the randomly selected group        

        user.save()
    except:
        print "Could not create user %s.%s" % (nl[0],nl[1])
        
# Create 100 randomly named instructors
g = Group.objects.get(name='instructors') 
for u in range(1,100):
    try:
        line = names[randint(1, len(names))]
        nl = line.split(',')
        username = "%s.%s" % (nl[0],nl[1])
        user = User.objects.create_user(username.lower(), 'user@example.com', 'testuser')
        user.first_name = nl[0]
        user.last_name = nl[1]
        user.is_staff() # Instructors get basic staff status
        g.user_set.add(user) # Add this student to the "Instructors" group
        user.save()
    except:
        print "Could not create user %s.%s" % (nl[0],nl[1]) 
        
