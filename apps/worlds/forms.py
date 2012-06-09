from django.db import models
from django.forms import ModelForm, Form
from django import forms
from worlds.models import World
from django.template.defaultfilters import slugify
from django.contrib.auth.models import User


class WorldForm(ModelForm):
    '''
    Form to allow creation of new worlds.
    '''

    class Meta:
        model = World
        fields = ('title','description','type','published','members',)
        

