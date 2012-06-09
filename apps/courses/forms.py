from django.db import models
from django.forms import ModelForm, Form
from django import forms
from courses.models import Offering
from django.contrib.auth.models import User


class CourseContactForm(Form):
    '''
    Form to allow students to contact instructors
    '''
    subject = forms.CharField(required=True, max_length=100)
    body = forms.CharField(widget=forms.Textarea,required=True)
        
