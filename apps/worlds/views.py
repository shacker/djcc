from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from worlds.models import World
from worlds.forms import WorldForm
from dynlists.forms import DynamicListForm
from datetime import datetime
from django.contrib import messages
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.core.urlresolvers import reverse
from django.db.models import Q
import copy
from django.template.defaultfilters import slugify
from utils.views import sanitizeHtml
from django.contrib.auth.decorators import user_passes_test


# Permissions definitions
def can_edit_worlds(user):
    return user.has_perm("worlds.edit_world")


@user_passes_test(can_edit_worlds)
def membership_list(request):
    """
    List of worlds to which I belong or am author of.
    """
    
    worlds = World.objects.filter(published=True,members__in=[request.user,])
    draft_worlds = World.objects.filter(published=False,created_by=request.user)    

    return render_to_response('worlds/memberships.html', locals(), context_instance=RequestContext(request))


@user_passes_test(can_edit_worlds)
def world_index(request,slug):
    """
    Home for a world
    """
    world = get_object_or_404(World,slug=slug)

    # Only world creators can see worlds in Draft status
    if world.published == False and world.created_by != request.user:
        return HttpResponseForbidden()
    else:
        return render_to_response('worlds/world_home.html', locals(), context_instance=RequestContext(request))


@user_passes_test(can_edit_worlds)
def create_world(request):
    """
    Create a new world (this will need permissions)
    """
    
    if request.POST:

        form = WorldForm(request.POST)
        if form.is_valid():
            # Don't commit the save until we've added in the fields we need to set
            world = form.save(commit=False)
            world.slug = slugify(world.title)
            world.created_date = datetime.now()
            world.created_by = request.user

            world.save()
            form.save_m2m()
            
            # World creator is automatically a member.
            world.members.add(request.user)            
           
            messages.success(request, "World [worldname] added!")  
            return HttpResponseRedirect(reverse('world_index',args=[world.slug]))            
        
    else:
        form = WorldForm()

    return render_to_response('worlds/world_create.html', locals(), context_instance=RequestContext(request))


@user_passes_test(can_edit_worlds)
def edit_world(request,world_slug):
    """
    Edit an existing world (this will need permissions)
    """
    world = get_object_or_404(World,slug=world_slug)

    if request.POST:

        form = WorldForm(request.POST, instance=world)
        if form.is_valid():
            # Don't commit the save until we've added in the fields we need to set
            world = form.save(commit=False)
            world.slug = slugify(world.title)                
            world.save()
            form.save_m2m()
           
            messages.success(request, "World [worldname] saved.")  
            return HttpResponseRedirect(reverse('world_index',args=[world.slug]))            
        
    else:
        form = WorldForm(instance=world)

    # Only world creators can edit worlds
    if world.created_by != request.user:
        return HttpResponseForbidden()
    else:
        return render_to_response('worlds/world_edit.html', locals(), context_instance=RequestContext(request))


