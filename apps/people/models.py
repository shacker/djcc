from django.db import models
from django.conf import settings
from django.contrib.auth.models import User, Group
from timezones.fields import TimeZoneField
from countries.models import Country
from django.contrib import admin
from django.contrib.localflavor.us.models import PhoneNumberField, USStateField
from people import constants
from datetime import datetime, date
from sorl.thumbnail import ImageField
from django.db.models import signals
from people.signals import create_profile, story_added
from django.template.defaultfilters import slugify
# from courses.models import Major
from django.core.urlresolvers import reverse


# Each Instructor belongs to one of these groups
INSTRUCTOR_GROUPS = ["Faculty","Visiting Scholars", "Lecturers", "Visiting Lecturers"]


def get_avatar_path(instance, filename):
    """
    Clean the filename and determine the foldername to upload avatars to.
    Must be defined before the Profile class.
    """

    # To keep filenames clean, take the first part of the filename and run it
    # through django's slugify function (if you run the whole thing through,
    # you lose the "." separator in the filename.)
    parts = str(filename).split(".")
    return 'upload/avatars/' + instance.user.username + '/' + slugify(parts[0]) + '.' + parts[1]


class Medium(models.Model):
    medium_id = models.IntegerField(primary_key=True)
    description = models.CharField(max_length=96)
    class Meta:
        db_table = u'medium'

    def __unicode__(self):
        return "%s" % (self.description)


class EmployeeProfileManager(models.Manager):
    """
    Only return staff and instructor profiles.
    """

    def get_query_set(self):

        return super(EmployeeProfileManager, self).get_query_set().filter(
            user__groups__name__in=
            ['Staff','IT Staff','Faculty','Faculty Emeritus','Lecturers','Visiting Lecturers','Web Team']
            )



class StaffProfileManager(models.Manager):
    """
    Only return staff profiles.
    """

    def get_query_set(self):
        return super(StaffProfileManager, self).get_query_set().filter(
            user__groups__name__in=
            ['Staff','IT Staff','Web Team']
            )


class ActiveProfileManager(models.Manager):
    """
    Manager for profiles where is_active is true in the user model.
    """

    def get_query_set(self):
        return super(ActiveProfileManager, self).get_query_set().filter(user__is_active=True)



class ActiveProfileAlumniManager(models.Manager):
    """
    Only return active alumni profiles.
    """

    def get_query_set(self):
        return super(ActiveProfileAlumniManager, self).get_query_set().filter(
                user__is_active=True,
                user__groups__name__in=['Alumni']
            )



class ProfileManager(models.Manager):
    pass


class ExtendActiveManager(models.Manager):
    """
    Manager for sub types where is_active is true in the user model.
    """

    def get_query_set(self):
        return super(ExtendActiveManager, self).get_query_set().filter(profile__user__is_active=True)

class BaseProfile(models.Model):
    """
    Place to put common stuff that extends Profile class.
    """

    class Meta:
        abstract = True

    def __unicode__(self):
        return self.profile.get_display_name()

    def get_form_name(self):
        return "%sForm" % self._meta.module_name.title()


class Profile(BaseProfile):
    """
    The base profile model which contains fields that pertain to everyone.
    Should be left out of the admin since only subclasses are created. (??? -sfh)

    Who is this person following?
    pr = Profile.objects.get(id=7455)
    pr.followees.all()

    Who is following this person?
    pr.followers.all()

    Add a new followee:
    otheruser = Profile.objects.get(id=38)
    pr.followees.add(otheruser)

    Remove a followee:
    pr.followees.remove(otheruser)
    """

    user = models.OneToOneField(User, primary_key=True)
    suffix = models.IntegerField(
                max_length=2,
                blank=True, null=True, choices=constants.PROFILE_SUFFIX_CHOICES)
    salutation = models.IntegerField(
                    max_length=2,
                    blank=True, null=True,
                    choices=constants.PROFILE_SALUTATION_CHOICES)
    middle_name = models.CharField(max_length=50, blank=True,null=True)
    title = models.CharField(blank=True,null=True, max_length=128)
    about = models.TextField(blank=True,null=True,help_text="A few sentences about yourself - capsule biography. No HTML allowed.")
    email2 = models.EmailField('Secondary Email', blank=True,null=True)
    home_phone1 = models.CharField('Home Phone',max_length=60, blank=True,null=True)
    biz_phone1 = models.CharField('Business Phone',max_length=60, blank=True,null=True)
    mobile_phone1 = models.CharField('Mobile Phone',max_length=60, blank=True,null=True)
    fax = models.CharField(max_length=60, blank=True,null=True)
    timezone = TimeZoneField()
    allow_contact = models.BooleanField(default=True,help_text='Allow the public to contact you through CalCentral.')
    show_name = models.BooleanField(default=True, help_text='Not currently implemented, for future use.')
    avatar = ImageField(upload_to=get_avatar_path, blank=True,null=True,
        help_text='Upload an avatar/image/icon to represent you on the site.<br />Please make sure your image is mostly square, not rectangular.')
    url_personal = models.URLField('Personal website',blank=True,null=True, verify_exists=True)
    url_org = models.URLField('Organization website',blank=True,null=True, verify_exists=True)
    accepted_terms = models.BooleanField(default=False,help_text="All users must accept our terms and conditions before doing anything on the site.")
    followees = models.ManyToManyField('self', blank=True,null=True,related_name='followers', symmetrical=False, help_text='People this person is following.')

    # Preferences
    email_on_follow = models.BooleanField(default=True,help_text='Receive email when someone follows you.')

    # Model Managers
    active_objects = ActiveProfileManager()
    alumni_objects = ActiveProfileAlumniManager()
    staff_objects = StaffProfileManager()
    emp_objects = EmployeeProfileManager()


    def __unicode__(self):
        return self.get_display_name()


    def get_display_name(self):
        if self.user.first_name and self.user.last_name: # and self.show_real_name:

            display_name = "%s %s" % (
                                self.user.first_name,
                                self.user.last_name,
                                )
            return display_name
        else:
            return self.user.username

    def phones_all(self):
        """
        Return a dict of all phone data.
        """
        return dict(home=self.home_phone1,
                    mobile=self.mobile_phone1,
                    work=self.biz_phone1)

    def is_staff(self):
        """
        Return True if the person is in the Staff group.
        Note: this is different from user.is_staff() which is a similar
        boolean flag that allows users to access the django admin.
        """
        if not self.user.is_active:
            return False
        #if self.user.is_staff(): return True
        if Group.objects.get(name="Staff") in self.user.groups.all():
            return True
        return False

    def is_instructor(self):
        """
        Return True if this person is in one of the Instructor groups.
        """
        if not self.user.is_active:
            return False
        for g in INSTRUCTOR_GROUPS:
            if Group.objects.get(name=g) in self.user.groups.all():
                return True
        return False

    def is_student(self):
        """
        Return True if this person is in the Student group.
        """
        if not self.user.is_active:
            return False
        if Group.objects.get(name="Students") in self.user.groups.all():
            return True
        return False

    def is_alumni(self):
        """
        Return True if this person is active and in the Alumni group.
        """
        if not self.user.is_active:
            return False
        if Group.objects.get(name="Alumni") in self.user.groups.all():
            return True
        return False

    def is_affiliated(self):
        """
        Need this in some places such as whether to show Private events (we
        don't show) them to alumni or to "basic" users.
        """
        if not self.user.is_active:
            return False
        if self.is_staff() or self.is_instructor() or self.is_student():
            return True
        return False

    def in_group(self,group):
        """
        Return True if the user/profile is in the group. Requires a string or a
        Group object as argument.
        """
        if type(group) == unicode or type(group) == str:
            return bool(self.user.groups.filter(name=group))

        if group in self.user.groups.all():
            return True

        return False

    def is_alumni_only(self):
        """
        Return True if a profile is only in the alumni group but not also staff
        or instructor.  Useful to rendering the correct nav, for example.
        """
        if self.is_alumni() and not self.is_staff() and not self.is_instructor():
            return True
        else:
            return False

    def get_form_name(self):
        return "%sForm" % self._meta.module_name.title()

    def get_primary_email(self):
        """
        Return user's primary email address.
        """
        return self.user.email


# When model instance is saved, trigger creation of corresponding profile
signals.post_save.connect(create_profile, sender=User)


class Staff(BaseProfile):
    """
    Staff extends profile, has one to one foreign key.
    """

    profile = models.OneToOneField(Profile, primary_key=True)
    office_num = models.CharField("Office",max_length=30, blank=True,null=True,help_text='Room number')
    #office = models.ForeignKey(Room)
    extension = models.CharField(blank=True,null=True, max_length=30,help_text='UC Berkeley Phone Extension #-####')

    objects = ProfileManager()
    active_objects = ExtendActiveManager()

    class Meta:
        verbose_name_plural = "Staff"

    def __unicode__(self):
        return self.profile.get_display_name()


class Instructor(BaseProfile):
    """
    Instructor profiles are used by everyone who teaches - Lecturers, Visiting
    Instructors, etc. TYPE of instructor is handled by their Group association.
    """

    profile = models.OneToOneField(Profile, primary_key=True)
    office_num = models.CharField(max_length=30, blank=True,null=True,help_text='Room number')
    extension = models.CharField(blank=True, null=True,max_length=30,help_text='UC Berkeley phone extension, e.g. 3-1234')
    bio_short = models.TextField(help_text="Required for all instructors; used on index pages. Limited to around 175 words.")
    bio_long = models.TextField(blank=True,null=True,help_text="Used on instructor detail pages.")

    objects = ProfileManager()
    active_objects = ExtendActiveManager()

    class Meta:
        verbose_name = "Instructor"
        verbose_name_plural = "Instructors"


class Student(BaseProfile):
    """
    A student profile has one to one with Profile
    """

    profile = models.OneToOneField(Profile, primary_key=True)
    grad_year = models.IntegerField('Graduation year',max_length=4,choices=constants.YEARS, blank=True, null=True)
    funding_amount = models.FloatField(blank=True,null=True,default=0)
    enrollment_date = models.DateField(blank=True,null=True)
    program_length = models.IntegerField(blank=True,null=True)
    visiting_scholar = models.BooleanField(default=False,help_text="Check box if this student is a visiting scholar.")
    majors = models.ManyToManyField('courses.Major',blank=True,null=True,related_name="studentmajors")

    objects = ProfileManager()
    active_objects = ExtendActiveManager()

    class Meta:
        verbose_name = "Student"


class Alumni(BaseProfile):
    """
    Alumni profile has one to one with Profile
    """

    profile = models.OneToOneField(Profile, primary_key=True)
    grad_year = models.IntegerField('Graduation year',max_length=4,choices=constants.YEARS, null=True)
    third_year = models.BooleanField('Is this student on the 3-year plan?',default=False)
    j200_inst = models.CharField(
                    'J200 Instructor',
                    blank=True,null=True,
                    max_length=100,
                    help_text='e.g. Gorney')
    funding_amount = models.FloatField(blank=True,null=True,default=0)
    enrollment_date = models.DateField(blank=True,null=True)
    program_length = models.IntegerField(blank=True,null=True)
    equipment_balance = models.FloatField(default=0.0)
    visiting_scholar = models.BooleanField(default=False,help_text="Check box if this student is a visiting scholar.")

    employer = models.CharField(blank=True,null=True, max_length=255)
    specialty = models.CharField(blank=True,null=True, max_length=128,help_text='e.g. Sports')
    medium = models.IntegerField(
                        max_length=4,
                        choices=constants.MEDIUM_CHOICES,
                        null=True,
                        blank=True)
    prev_emp1 = models.CharField('Previous Employer #1',max_length=384,blank=True,null=True,)
    prev_emp2 = models.CharField('Previous Employer #2',max_length=384,blank=True,null=True,)
    prev_emp3 = models.CharField('Previous Employer #3',max_length=384,blank=True,null=True,)

    notes_exclude = models.BooleanField(
                                'Exclude notes',
                                default=False,
                                help_text='Please do NOT include my notes in the alumni newsletter.',
                                blank=True)
    notes = models.TextField(
                    blank=True,
                    null=True,
                    help_text="Tell us what you're up to, or add general notes on your life, whereabouts and recent projects.")
    mod_date = models.DateField(auto_now=True)
    pub_display = models.BooleanField(
                                'Display Option',
                                default=True,
                                help_text='If unchecked, record will be hidden even from other J-School alumni, faculty, students and staff.')
    freelance = models.BooleanField(
                                'Freelancing?',
                                default=False,)
    region = models.IntegerField(max_length=4,choices=constants.REGION_CHOICES,null=True,blank=True)
    prev_intern1 = models.CharField('Previous Intership 1',max_length=384,blank=True,null=True,)
    prev_intern2 = models.CharField('Previous Intership 1',max_length=384,blank=True,null=True,)
    prev_intern3 = models.CharField('Previous Intership 1',max_length=384,blank=True,null=True,)
    first_job = models.CharField(
                    'First job out of J-School',
                    max_length=384,
                    blank=True,null=True,)
    books = models.TextField(blank=True,null=True,)
    deceased_notes = models.CharField(blank=True,null=True, max_length=255)
    mia = models.BooleanField(
                    default=False,
                    help_text='Unable to contact this person, whereabouts unknown.')
    mia_notes = models.TextField(blank=True,null=True,)
    interview = models.BooleanField(default=False,help_text='Has this person been interviewed [for xxx?]')

    interview_year = models.IntegerField(choices=constants.YEARS,default=0)
    interview_notes = models.TextField(blank=True,null=True)
    agents_year = models.IntegerField(choices=constants.YEARS,default=0,help_text='Not sure what this field is for?',blank=True,null=True,)
    agents_notes = models.TextField(help_text='Not sure what this field is for?',blank=True,null=True,)
    event_attend_notes = models.TextField(blank=True,null=True)
    famous_notes = models.TextField(blank=True,null=True)

    volunteer_speak = models.BooleanField(
                                default=False,
                                help_text="I'm happy to speak with current students about my career path, what it's like to work at my news outlet (or as a freelancer) and what sort of internship opportunities exist in my workplace.")

    volunteer_committee = models.BooleanField(
                                default=False,
                                help_text="I'd like to volunteer to get more involved with planning events and alumni outreach. I might even have suggestions for events in my area.")
    volunteer_interview = models.BooleanField(
                                default=False,
                                help_text="I'd like to interview students in my area to help with the admissions process.")
    volunteer_mentor = models.BooleanField(
                                default=False,
                                help_text="I'd like to be matched with a student during the school year to provide additional career guidance.")
    volunteer_agent = models.BooleanField(
                                default=False,
                                help_text="I'd like to be a Class Agent and serve as a liason between the Alumni Board and my graduating classes.")
    maillist_class = models.BooleanField(
                                default=False,
                                help_text="Please add me to my class email list.")
    no_maillists = models.BooleanField(
                                default=False,
                                help_text="I do NOT want to receive any email from the journalism school. Please make sure I am NOT on any of the mailing lists.")
    no_reminder = models.BooleanField(
                                default=False,
                                help_text="I would like to opt-out from the twice yearly reminder email.")

    suggestions = models.TextField(
                                blank=True,
                                null=True,
                                help_text="Do you have suggestions for us about what you'd like to get out of the J-School Alumni Organization? If so, please write us a note and we'll try to incorporate your idea.")
    committee_notes = models.TextField(blank=True,null=True)
    inactive = models.BooleanField(default=False)
    revision = models.IntegerField(help_text='This field should increment up when record is updated.',blank=True,null=True)

    objects = ProfileManager()
    active_objects = ExtendActiveManager()

    class Meta:
        verbose_name = "Alumni"
        verbose_name_plural = "Alumni"


class Donation(models.Model):
    '''
    Donations by anyone (not just alums can donate - anyone can)
    '''
    profile = models.ForeignKey(Profile)
    amount = models.IntegerField()
    date = models.DateField()
    description = models.CharField(max_length=765, blank=True,null=True)
    notes = models.TextField(blank=True,null=True)
    class Meta:
        db_table = u'people_donation'

    def __unicode__(self):
        return self.profile.__unicode__()


class Address(models.Model):
    """
    People's Addresses - they can have more than one.
    """

    profile = models.ForeignKey(Profile)
    address_type = models.IntegerField(max_length=2,choices=constants.ADDRESS_TYPE_CHOICES)
    street_1 = models.CharField(max_length=200, blank=True,null=True)
    street_2 = models.CharField(max_length=200, blank=True,null=True)
    street_3 = models.CharField(max_length=200, blank=True,null=True)
    city = models.CharField(max_length=200)
    state = USStateField(blank=True,null=True)
    state_other = models.CharField(max_length=384,blank=True,null=True,help_text='Useful for international addresses.')
    postal_code = models.CharField(max_length=50,blank=True,null=True)
    country  = models.ForeignKey(Country,blank=True,null=True)
    display = models.BooleanField(default=True, help_text="Display this address on my profile page")

    def __unicode__(self):
        return "%s %s, %s" % (self.street_1, self.city, self.state)

    class Meta:
        verbose_name = "Address"
        verbose_name_plural = "Addresses"

    def get_form_name(self):
        return "%sForm" % self._meta.module_name.title()




class Award(models.Model):
    """
    People's Awards.
    """

    profile = models.ForeignKey(Profile)
    title = models.CharField(max_length=200,blank=True,null=True)
    description = models.TextField(blank=True,null=True)
    date_received = models.DateField(blank=True,null=True,help_text="Please enter dates in this format: 1986-09-13 for Sept. 13 1986.")
    display = models.BooleanField(default=True, help_text="Display item on my public profile page")

    def __unicode__(self):
        return self.title

    class Meta:
        ordering = ['-date_received']


class Reference(models.Model):
    """
    People's references (e.g. for resumes).
    """

    profile = models.ForeignKey(Profile)
    body = models.TextField()

    def __unicode__(self):
        return self.profile.__unicode__()




class Experience(models.Model):
    """
    People's experience.
    """
    profile = models.ForeignKey(Profile)
    experience_type = models.IntegerField(
                        max_length=3,
                        choices=constants.EXPERIENCE_TYPE_CHOICES,
                        blank=True,null=True)
    title = models.CharField(max_length=200,help_text="Title you held at this job or internship.",blank=True,null=True)
    description = models.TextField(help_text="Summary of the experience.",blank=True,null=True)
    company = models.CharField(max_length=200,blank=True,null=True,help_text="Company or organization name.")
    city = models.CharField(max_length=200,blank=True,null=True)
    state = USStateField(blank=True,null=True)
    country  = models.CharField(max_length=200,blank=True,null=True)
    start_date = models.DateField(blank=True,null=True,help_text="Please enter dates in this format: 1986-09-13 for Sept. 13 1986.")
    end_date = models.DateField(blank=True,null=True,help_text="Please enter dates in this format: 1986-09-13 for Sept. 13 1986.")
    display = models.BooleanField(default=True, help_text="Display item on my public profile page")


    def __unicode__(self):
        return "%s, %s" % (self.title, self.company)

    class Meta:
        ordering = ['-start_date']



class Skill(models.Model):
    """
    People's skills.
    """

    profile = models.ForeignKey(Profile)
    summary = models.TextField()
    display = models.BooleanField(default=True, help_text="Display item on my public profile page")

    def __unicode__(self):
        return u"%s ..." % self.summary[:25]

    # def __unicode__(self):
    #     return self.profile.__unicode__()

class Education(models.Model):
    """
    People's education.
    """

    profile = models.ForeignKey(Profile)
    diploma = models.IntegerField(
                        max_length=3,
                        choices=constants.EDUCATION_TYPE_CHOICES,
                        blank=True,null=True)
    school = models.CharField(max_length=200,blank=True,null=True)
    description = models.TextField(blank=True,null=True,help_text="Summary of education period.")
    start_date = models.DateField(blank=True,null=True,help_text="Please enter dates in this format: 1986-09-13 for Sept. 13 1986.")
    end_date = models.DateField(blank=True,null=True,help_text="Please enter dates in this format: 1986-09-13 for Sept. 13 1986.")
    display = models.BooleanField(default=True, help_text="Display item on my public profile page")

    class Meta:
        verbose_name_plural = "Education"
        ordering = ['-start_date']

    def __unicode__(self):
        return self.school



