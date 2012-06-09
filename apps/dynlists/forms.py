from django.db import models
from django.forms import ModelForm, Form
from django import forms
from dynlists.models import DynamicList
from django.template.defaultfilters import slugify
from django.contrib.auth.models import User



class DynamicListForm(ModelForm):
    '''
    Form to allow creation/editing of new DynamicLists
    '''
    addl_members = forms.ModelMultipleChoiceField(queryset=User.objects.all(),label="Additional Members",required=False)
    admins = forms.ModelMultipleChoiceField(queryset=User.objects.all(),label="Additional Admins",required=False)
    
    class Meta:
        model = DynamicList
        fields = ('dl_name','description','majors','admins','addl_members',)
        
