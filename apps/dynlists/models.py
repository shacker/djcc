from django.db import models
from django.contrib.auth.models import User
from courses.models import Major
from people.models import Student
from autoslug import AutoSlugField
import datetime
from django.db.models import Q
from itertools import islice, chain


class DynamicList(models.Model):
    """Defines a mailing list for one or more classes/programs/individuals"""
    dl_name = models.CharField('Title',blank=False, max_length=100)
    description = models.TextField(blank=False)
    created_by = models.ForeignKey(User,related_name='dl_created_by')
    created_date = models.DateTimeField(default=datetime.datetime.now)
    modified_date = models.DateTimeField(default=datetime.datetime.now)    
    majors = models.ManyToManyField(Major,related_name='majors',blank=True)
    admins = models.ManyToManyField(User,related_name='dl_admins')
    addl_members = models.ManyToManyField(User,related_name='dl_members',blank=True,
        help_text='Dynamic Lists usually consist of Programs or Majors, but individual users can belong too.')

    def __unicode__(self):
        return self.dl_name
        
    def get_members(self):
        '''
        Obtain all members of this dynamic list, which includes its creator,
        all manually added members, and all designated admins. Should also
        include all members of all majors or classes or courses or programs we set it up to handle.
        
        We can't combine disparate queries easily, but we can get IDs of all members
        of each set and then do a single queryset for users with those IDs. 
        '''
        
        all_members = set()
        
        # Designated admins
        for u in self.admins.all():
          all_members.add(u.id)
        
        # Desginated additional members
        for u in self.addl_members.all():
          all_members.add(u.id)
        
        # Make sure this DL's creator is always a member!
        all_members.add(self.created_by.id)
        
        # All students in all majors associated with this DL
        students = Student.objects.filter(majors__in=self.majors.all())
        for s in students:
            all_members.add(s.profile.user.id)

        return User.objects.filter(pk__in=all_members)
