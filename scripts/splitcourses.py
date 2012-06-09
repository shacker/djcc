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

tempset = []
allofferings = Offering.objects.all()

for a in allofferings:
    tempset.append(a.ccn)
    
print tempset
print len(tempset)

# Now reduce tempset down to distinct CCNs
tempset = set(tempset)

print tempset
print len(tempset)

# tempset is now just the unique CCNs. We'll make a Course instance for each by 
# getting the first result of a query for Offerings with that CCN

for t in tempset:
    o = Offering.objects.filter(ccn=t)[:1]
    # o looks like a single object but is actually a queryset consisting of one record.
    # To  get the first actual object in it, use o[0]
    offering = o[0]
    print
    print offering
    
    # Create a Course record based on that
    course = Course()
    course.title = offering.title
    course.ccn = offering.ccn
    course.cstring = offering.cstring
    course.units = offering.units
    course.type = offering.type
    course.description = offering.description
    course.restrictions = offering.restrictions
    course.save()
    
    # Programs is many to many. Loop through and re-create
    for p in offering.programs.all():
        course.programs.add(p)
        
    # title = models.CharField(max_length=384)
    # ccn = models.CharField('CCN',max_length=384, blank=True)
    # cstring = models.ForeignKey(Cstring,verbose_name='Course String',help_text="e.g. J-200, but without the J")
    # units = models.IntegerField(choices=constants.UNIT_TYPE_CHOICES)
    # type = models.IntegerField(choices=constants.COURSE_TYPE_CHOICES)
    # description = models.TextField()
    # restrictions = models.TextField(null=True,blank=True)
    # programs = models.ManyToManyField(Program,blank=True)
    

    