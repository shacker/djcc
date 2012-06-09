from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from news.models import Story

def story_list(request):
    """
    Simple index of recent news
    """
    
    stories = Story.objects.all()

    return render_to_response('news/index.html', locals(), context_instance=RequestContext(request))



def story_detail(request,story_id):
    """
    Individual story view
    """
    
    story = get_object_or_404(Story,pk=story_id)

    return render_to_response('news/story.html', locals(), context_instance=RequestContext(request))

