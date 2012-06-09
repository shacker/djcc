from django.db import models
import datetime
from django.contrib.auth.models import User
from django.conf import settings
import os

FILE_PERMISSION_CHOICES = (
    ('single','Just Me'),
    ('shared','People I share it with'),
    ('calcentral','Logged-in users only'),
    ('world','Visible to the world'),
)

# def upload_path():
#     return '%supload/libraries' % (settings.MEDIA_URL)


class MimeType(models.Model):
    '''Define allowable extensions and their mimetypes'''
    extension = models.CharField(max_length=4)
    mimetype = models.CharField(max_length=40)

    class Meta:
        verbose_name_plural = "MimeTypes"

    def __unicode__(self):
        return self.mimetype


class StandardFile(models.Model):
    """
    Single files uploaded by users and stored in their Library or shared with others.
    """

    file = models.FileField(upload_to='upload/libraries',max_length=120)
    title = models.CharField(blank=True,null=True,max_length=60)
    added_by = models.ForeignKey(User)
    added_on = models.DateTimeField(blank=True,null=True,default=datetime.datetime.now)
    mimetype = models.ForeignKey(MimeType)
    permissions = models.CharField(choices=FILE_PERMISSION_CHOICES,max_length=10)
    modified = models.DateTimeField(blank=True, null=True,default=datetime.datetime.now)

    class Meta:
        verbose_name_plural = "Files"

    def __unicode__(self):
        if self.title:
            return self.title
        else:
            return os.path.basename(self.file.name)



class FileShare(models.Model):
    """
    Lookup table for files shared with individuals or groups (groups not yet implemented)
    """

    file = models.ForeignKey(StandardFile)
    shared_with = models.ForeignKey(User)

    class Meta:
        verbose_name_plural = "File Shares"

    def __unicode__(self):
        if self.file.title:
            return self.file.title
        else:
            return os.path.basename(self.file.title.name)


