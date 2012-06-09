from django import forms
from django.db import models


class TermsForm(forms.Form):
    
    '''
    These two fields aren't on the Profile model.
    Instead, we ask user to accept both fields in home.views.check_accepted_terms,
    then set profile.accepted_terms = True if they do.    
    '''
    
    agree = forms.BooleanField()
    concur = forms.BooleanField()    
