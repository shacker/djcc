from django.db import models
from django import forms
from django.forms import ModelForm, Form, ModelChoiceField
from notifications.models import Notification
from dynlists.models import DynamicList
from django.db.models import Q


class NotificationForm(ModelForm):
    '''
    Used for creating or editing Notifications
    '''
    
    # Request object is not accessible from a form, but we need it for the
    # set of Dynamic Lists, so we pass in 'user' from the view and override the form constructor.
    # Via http://mikethecoder.com/post/5865162520/django-form-request-user.
    # Thinking a better way to do this might be to use a ModelManager for DynamicLists.
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(NotificationForm, self).__init__(*args, **kwargs)
        u = self.user        
    
        # To display set of allowed DynamicLists, find all DynamicLists
        # the current user either created or is a designated admin of
        # with a Q object, then pass its output into the set of named fields.
        
        dlists = DynamicList.objects.filter( Q(created_by=u) | Q(admins__in=[u,]) ).distinct()
        self.fields['dlist'] = forms.ModelChoiceField(queryset=dlists,label='Distribution List',required=False)
    
    class Meta:
        model = Notification
        fields = (
            'title',
            'type',
            'required',
            'event_due_date',
            'place',
            'send_date',
            'dlist',
            'offering',
            'description',
            )