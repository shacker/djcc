from django.template import RequestContext
from django.shortcuts import render_to_response
from django.contrib import messages
from news.models import Story
from notifications.models import Delivered

def dashboard(request):
    """
    Display user dashboard
    """
    stories = Story.objects.all().order_by('pubdate')[:5]
    tasks = Delivered.objects.filter(user=request.user,notification__type='task')[:5]
    events = Delivered.objects.filter(user=request.user,notification__type='event')[:5]
    
    return render_to_response(
        'dashboard/dashboard.html', 
        locals(), 
        context_instance=RequestContext(request)
        )
   
