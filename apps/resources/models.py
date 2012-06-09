from django.db import models

class Resource(models.Model):
    """
    Base class for resource models.  A resource is defined as something that
    you would reserve.  i.e. Room or EquipmentKit
    """
    name = models.CharField(max_length=100)
    notes = models.TextField(blank=True,)
    ordering = models.IntegerField(blank=True, default=1000,
        help_text='If set, will establish the order in which resources appear on the calendar grid. Recommended using integers like 10,20,30, etc.')

    def __unicode__(self):
        return self.name

    def is_available(self):
        """
        Return True or False, call the child method.
        """
        try:
            return self.kit.is_available()
        except:
            try:
                return self.room.is_available()
            except:
                pass
        return False



class Room(Resource):
    """
    A resource subclass to define rooms.
    """ 

    number = models.CharField("Room Number",max_length=64,blank=True)
    has_screen = models.BooleanField()

    def __unicode__(self):
        return "%s %s" % (self.name, self.number)

    def is_available(self):
        return True

