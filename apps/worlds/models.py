from django.db import models
from django.contrib.auth.models import User
from courses.models import Major
from people.models import Student
from autoslug import AutoSlugField
import datetime
from django.db.models import Q
from itertools import islice, chain


class WorldType(models.Model):
    """Defines subtypes of worlds"""
    world_type_name = models.CharField(blank=False, max_length=100)
    slug = models.SlugField()

    def __unicode__(self):
        return self.world_type_name


class World(models.Model):
    """
    Base class for all major member groupings.
    Should never directly contain members - users only belong to subclasses of World.
    """

    title = models.CharField(max_length=120)
    # slug = models.SlugField(unique=True)
    slug = AutoSlugField(unique=True,populate_from='title')
    description = models.TextField(blank=True)
    created_date = models.DateTimeField(blank=True, default=datetime.datetime.now)
    created_by = models.ForeignKey(User,related_name='world_created_by')
    published = models.BooleanField(default=False,blank=True)
    type = models.ForeignKey(WorldType)
    members = models.ManyToManyField(User,related_name='members')

    class Meta:
        verbose_name_plural = "Worlds"

    def __unicode__(self):
        return self.title


