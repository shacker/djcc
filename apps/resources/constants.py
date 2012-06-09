# Constant 
ACTIVITY_CHOICES = ( (1,'Checkout'),
                     (2,'Check-in'), )

STATUS_CHOICES_AVAILABLE = 'is'
STATUS_CHOICES_OUT_OF_SERVICE = 'os'
STATUS_CHOICES = ((STATUS_CHOICES_AVAILABLE, 'In Service'),
                  (STATUS_CHOICES_OUT_OF_SERVICE, 'Out of Service'),)

# Constant 
ACTIVITY_CHOICES = ( 
    ('so','Sent out for repair.'),
    ('pr','Problem reported.'),)

TIME_CHOICES = (
    ('08:00:00','8:00am'),
    ('09:00:00','9:00am'),
    ('10:00:00','10:00am'),
    ('11:00:00','11:00am'),
    ('12:00:00','Noon'),
    ('13:00:00','1:00pm'),
    ('14:00:00','2:00pm'),
    ('15:00:00','3:00pm'),
    ('16:00:00','4:00pm'),
    ('17:00:00','5:00pm'),
    ('18:00:00','6:00pm'),
    ('19:00:00','7:00pm'),
    ('20:00:00','8:00pm'),
    )

CATEGORY_CHOICES = (
    ('vi','Video'),
    ('au', 'Audio'),
    ('ph', 'Photo'),
    ('mi', 'Misc'))

EQUIP_CATS = (
    ('vcm', 'Video Cameras',),
    ('pcm', 'Photo Cameras',),
    ('aud', 'Audio Recorders',),
    ('dvd', 'DVD/VHS Players',),
    ('prj', 'Projectors',),
    ('rad', 'Radios',),
    ('trp', 'Tripods',),
    ('mic', 'Microphones',),
    ('msc', 'Miscellaneous',),
    ('scn', 'Scanners',),
    ('lap', 'Laptops',),
    ('hdp', 'Headphones',),
    ('cbl', 'Cables',),)
