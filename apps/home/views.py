from django.template import RequestContext
from django.shortcuts import render_to_response
# from django.utils.translation import ugettext as _
from news.models import Story
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.contrib import messages

def home(request):
    """
    Display homepage (logged in or not)
    """
    stories = Story.objects.all().order_by('pubdate')[:3]
    no_sidebar = True

    return render_to_response('home/home.html', locals(), context_instance=RequestContext(request))
   
   
    
def check_accepted_terms(request):
    """
    Check whether user has accepted terms of service.
    Anon users get sent to login page.
    Auth users get sent to homepage if accepted before, or get the Acceptance form if not.
    Both fields in home.forms.TermsForm must be satisfied before submission will be accepted.
    """
    
    if request.user.is_authenticated():

        # Import here since this is rarely used.
        from home.forms import TermsForm
        profile = request.user.get_profile()

        if request.user.get_profile().accepted_terms == True:
            return HttpResponseRedirect(reverse('dashboard'))        

        else:            
            if request.POST:
                form = TermsForm(request.POST)
                if form.is_valid():
                    profile.accepted_terms = True
                    profile.save()

                    messages.success(request, "Thanks and welcome to CalCentral!")  
                    return HttpResponseRedirect(reverse('dashboard'))            

            else:
                form = TermsForm()
            
            return render_to_response('registration/terms.html', locals(), context_instance=RequestContext(request))    
        
    else:
        # Not logged in - redirect to login
        return HttpResponseRedirect(reverse('login'))        

    