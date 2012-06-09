from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from dynlists.models import DynamicList
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
def can_edit_dynlists(user):
    return user.has_perm("dynlists.edit_dynlist")

# Begin utility functions used by dynamic lists

@user_passes_test(can_edit_dynlists)
def dl_copy(request,items):
    '''
    Makes a COPY of each selected dynamic list
    '''

    for i in items:
        new_item = copy.copy(i)
        new_item.id = None # Prevent primary key collisions
        new_item.dl_name = 'Copy of %s' % i.dl_name
        new_item.modified_date = datetime.now()
        new_item.save()
        messages.success(request, "Copy of %s created." % i.dl_name)
        
@user_passes_test(can_edit_dynlists)
def dl_delete(request,items):
    '''
    Delete each selected dynamic list
    '''
    for i in items:
        i.delete()
        messages.success(request, "List %s was deleted." % i.dl_name)        

# End utility functions used by dynamic lists 

@user_passes_test(can_edit_dynlists)
def dynamic_list_index(request):
    """
    Home for Dynamic Lists
    """
    if request.method == 'POST':

        # Convert POST array into list, then select matching records as queryset
        selected = request.POST.getlist('dlist_list')
        items = DynamicList.objects.filter(id__in=selected)

        if 'copy' in request.POST:
            dl_copy(request,items)
            return HttpResponseRedirect(reverse('dynamic_lists'))

        elif 'delete' in request.POST:
            dl_delete(request,items)
            return HttpResponseRedirect(reverse('dynamic_lists'))
            
        else:
            pass

        # Redirect to this view so user can't accidentally resubmit with browser Refresh
        return HttpResponseRedirect(reverse('dynamic_lists'))    
    
    # To display set of allowed DynamicLists, find all DynamicLists
    # the current user either created or is a designated admin of
    # with a Q object, then pass its output into the set of named fields.
    
    u = request.user
    dlists = DynamicList.objects.filter( Q(created_by=u) | Q(admins__in=[u,]) ).distinct()

    return render_to_response(
        'worlds/dl_index.html', 
        locals(), 
        context_instance=RequestContext(request)
        )

@user_passes_test(can_edit_dynlists)
def dl_edit(request,dl_id=None):
    """
    Create or edit an existing dynamic list in a single view. 
    A bit verbose, but better than using two view functions for similar tasks.
    """
    
    dlist = get_object_or_404(DynamicList,pk=dl_id) if dl_id else None

    if request.POST:
        form = DynamicListForm(request.POST or None, instance=dlist)

        if form.is_valid():
            list = form.save(commit=False)
            list.dl_name = form.cleaned_data['dl_name']
            list.description = sanitizeHtml(form.cleaned_data['description'])
            list.created_by = request.user
            if not list.created_date:
                list.created_date = datetime.now()
            list.modified_date = datetime.now()
            list.save()
            form.save_m2m()

            messages.success(request, "%s was changed." % list.dl_name)
            return HttpResponseRedirect(reverse('dynamic_lists'))

    # Handle both bound and unbound forms
    else:
        try:
            dlist
            form = DynamicListForm(instance=dlist)
        except:
            form = DynamicListForm()


    return render_to_response('worlds/dl_edit.html', locals(), context_instance=RequestContext(request))
