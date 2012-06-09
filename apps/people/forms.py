import re
from django import forms
from django.contrib.auth.models import User
from django.utils.safestring import mark_safe
from django.contrib.localflavor.us.forms import USStateField
from people.models import Staff, Profile, Instructor, Alumni, Student,\
                          Address, Skill, Experience, Skill, \
                          Award, Education
from people.constants import STATE_CHOICES_WITH_NULL, YEARS, REGION_CHOICES, STATE_CHOICES

# Define phone fields here on profile model that need custom validation
PHONE_FIELDS = ('home_phone1', 'mobile_phone1', 'biz_phone1')
PHONE_RE = re.compile(r'^((\d{1,4}[- ]+\d{1,3})|(\d{2,3}))[- ]+(\d{3,4})[- ]+(\d{4})')
PHONE_HELP = "312-567-8912 (US) or 55-11-3312-3412 (Int'l)"


class FileWidget(forms.FileInput):
    """
    Swiped from django admin.  Maybe all our media forms could inheret
    this.  TODO 
    """

    def __init__(self, attrs={}):
        super(FileWidget, self).__init__(attrs)

    def render(self, name, value, attrs=None):
        output = []
        if value and hasattr(value, "url"):
            output.append('%s <a target="_blank" href="%s">%s</a> <br />%s ' % \
                ('Currently:', value.url, value, 'Change:'))
        output.append(super(FileWidget, self).render(name, value, attrs))
        return mark_safe(u''.join(output))

class AddressForm(forms.ModelForm):
    
    state = USStateField( widget=forms.Select(choices=STATE_CHOICES_WITH_NULL), required=False)

    class Meta:
        model = Address
        exclude = ('profile','latitude','longitude')
        
class AwardsForm(forms.ModelForm):
    
    class Meta:
        model = Award
        
class SkillsForm(forms.ModelForm):
    
    class Meta:
        model = Skill        

class ProfileForm(forms.ModelForm):
    """
    Base class for all profiles includes field for primary email that
    populates back to User object.
    """

    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)
        try:
            self.fields['email'].initial = self.instance.user.email
        except User.DoesNotExist:
            pass

    email = forms.EmailField()
    avatar = forms.FileField(
                    help_text="Should be at least 200px wide. Please use a real image of yourself.",
                    widget=FileWidget,
                    required=False)

    class Meta:
        model = Profile
        fields = (
                 'suffix',
                 'salutation',
                 'title',
                 'about',
                 'avatar',
                 'email',
                 'email2',
                 'home_phone1',
                 'biz_phone1',
                 'mobile_phone1',
                 'fax',
                 'timezone',
                 'allow_contact',
                 'url_personal',
                 'url_org',)

    def _clean_phone(self, fieldname, value):
        """
        Take a fieldname and value for a phone field and make sure 
        it validates according to our regex.
        """
        if not value:
            return u''
        if not re.match(PHONE_RE,value):
            self._errors[fieldname] = [ u'Please use a format like %s'% PHONE_HELP ]
        return value

    def save(self, *args, **kwargs):
        """
        Handle the user email field as well.
        """
        u = self.instance.user
        u.email = self.cleaned_data['email']
        u.save()
        profile = super(ProfileForm, self).save(*args,**kwargs)
        return profile
        
    def clean(self):
        """
        Do some custom field validation.
        """
        for f in PHONE_FIELDS:
            if self.cleaned_data[f]:
                self.cleaned_data[f] = self._clean_phone(
                                            f, self.cleaned_data[f])
        return self.cleaned_data
            

class StaffForm(forms.ModelForm):
    """
    Extended form staff 
    """

    class Meta:
        model = Staff
        exclude = ('profile',)

class StudentForm(forms.ModelForm):
    """
    Extended form for student 
    """

    grad_year = forms.IntegerField(required=False)


    class Meta:
        model = Student
        exclude = ('profile','equipment_balance')

class InstructorForm(forms.ModelForm):
    """
    Extended form for instructors
    """

    class Meta:
        model = Instructor
        exclude = ('profile',)


class AlumniAdminForm(forms.ModelForm):
    """
    Alumni form for admins, contains all fields.
    """

    class Meta:
        model = Alumni
        exclude = ('revision',)


class AlumniForm(forms.ModelForm):
    """
    Alumni form for alumni to edit their own data.
    """

    class Meta:
        model = Alumni
        fields = (
            'pub_display',
            'volunteer_agent',
            'volunteer_speak',
            'volunteer_committee',
            'volunteer_interview',
            'volunteer_mentor',
            'maillist_class',
            'no_reminder',
            'no_maillists',
            'suggestions',
            'freelance',
            'employer',
            'specialty',
            'first_job',
            'prev_intern1',
            'prev_intern2',
            'prev_intern3',
            'notes_exclude',
            'notes')


class AwardForm(forms.ModelForm):

    class Meta:
        model = Award
        exclude = ('profile',)



class ExperienceForm(forms.ModelForm):

    state = USStateField( widget=forms.Select(choices=STATE_CHOICES_WITH_NULL), required=False)

    class Meta:
        model = Experience
        exclude = ('profile','latitude','longitude')
    

class SkillForm(forms.ModelForm):

    class Meta:
        model = Skill
        exclude = ('profile',)

class EducationForm(forms.ModelForm):

    class Meta:
        model = Education
        exclude = ('profile',)

class AlumniQueryForm(forms.Form):

    YEAR_CHOICES = [('','---------')]
    YEAR_CHOICES.extend(YEARS)
    
    STATE_CHOICES_W_NULL = [('','---------')]
    STATE_CHOICES_W_NULL.extend(STATE_CHOICES)

    q = forms.CharField(
            label='Name/Keywords', 
            required=False, )
            #help_text='Searches first, last name, username and email address.')
    alumni__grad_year = forms.ChoiceField(
                            label='Grad Year', choices=YEAR_CHOICES, required=False)
    alumni__employer__icontains = forms.CharField(
                            label='Employer',required=False)
    address__city__icontains = forms.CharField(
                            label='City',required=False)
    address__state = forms.ChoiceField(
                            label='State', 
                            choices=STATE_CHOICES_W_NULL, required=False)    
                            
class QueryForm(forms.Form):


    TYPE_CHOICES = (
        ('','---------'),
        (2,'Students'),
        (4,'Faculty'),
        (3,'Staff'),
        (5,'Lecturers'),
        (11,'Visiting Lecturers'),
        (6,'Visiting Scholars'),)

    q = forms.CharField(label='Name/Keywords', required=False)
    type = forms.ChoiceField(choices=TYPE_CHOICES, required=False)
    alum = forms.BooleanField(
                    label='Include Alumni?', 
                    required=False,)
    inactive = forms.BooleanField(
                    label='Include inactive users?', 
                    required=False,)                    
                    
