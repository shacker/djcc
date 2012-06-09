from django.db import models
import datetime
from dynlists.models import DynamicList
from courses.models import Offering
from django.contrib.auth.models import User



NOTIFICATION_TYPE_CHOICES = (
    ('task', 'Task'),
    ('event', 'Event'),
)

NOTIFICATION_STATE_CHOICES = (
    ('draft', 'Draft'),
    ('queue', 'Queue'),
    ('arch', 'Archive'),
    ('trash', 'Trash'),        
)

class Notification(models.Model):
    """
    Shared data model for Tasks and Events. This model is manipulated
    by instructors and staff. When a notification instance is in
    queue state and has been processed, a child record is created
    for each user in the delivery queue.
    """
    type = models.CharField(choices=NOTIFICATION_TYPE_CHOICES,max_length=6)        
    title = models.CharField(blank=False, max_length=120)
    author = models.ForeignKey(User)
    required = models.BooleanField(default=True)
    event_due_date = models.DateTimeField(blank=False, default=datetime.datetime.now)
    place = models.CharField(blank=True,null=True,max_length=120)    
    send_date = models.DateTimeField(blank=False, default=datetime.datetime.now)
    dlist = models.ForeignKey(DynamicList,blank=True,null=True)
    offering = models.ForeignKey(Offering,blank=True,null=True)    
    description = models.TextField()
    state = models.CharField(blank=False, max_length=6, choices=NOTIFICATION_STATE_CHOICES)        
    
    class Meta:
        verbose_name_plural = "Notifications"  

    def __unicode__(self):
        return self.title


class Delivered(models.Model):
    """
    A foreign key reference to Notification, delivered to *each*
    user in the delivery range for a parent notification
    """
    notification = models.ForeignKey(Notification)
    user = models.ForeignKey(User)
    completed = models.BooleanField(default=False)
    deliver_date = models.DateTimeField(blank=False, default=datetime.datetime.now)
    
    class Meta:
        verbose_name_plural = "Delivered Notifications"  

    def __unicode__(self):
        return self.notification.title       
 
