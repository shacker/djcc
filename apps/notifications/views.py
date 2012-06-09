from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib import messages
from notifications.models import Notification, Delivered
from notifications.forms import NotificationForm
from postman.models import Message, STATUS_PENDING, STATUS_ACCEPTED
from utils.views import sanitizeHtml
import copy
import datetime
from django.contrib.auth.decorators import user_passes_test


# Permissions definitions
def can_edit_notifications(user):
    return user.has_perm("notifications.edit_notification")



### Begin reusable functions for notifications
def enqueue(request,items):
    '''
    Sets state of all members of queryset "items" to "queue"
    '''
    for i in items:
        i.state = 'queue'
        i.save()
        messages.success(request, "%s moved to queue." % i.title)

def endraft(request,items):
    '''
    Sets state of all members of queryset "items" to "draft"
    '''
    for i in items:
        i.state = 'draft'
        i.save()
        messages.success(request, "%s moved to Drafts." % i.title)

def copy_to_drafts(request,items):
    '''
    Makes a draft COPY of each member of queryset "items"
    '''
    for i in items:
        new_item = copy.copy(i)
        new_item.id = None # Prevent primary key collisions
        new_item.title = 'Copy of %s' % i.title
        new_item.save()
        messages.success(request, "%s moved to drafts." % i.title)
        
def trash(request,items):
    '''
    Moves each member of queryset "items" to trash
    '''
    for i in items:
        i.state = 'trash'
        i.save()
        messages.success(request, "%s moved to trash." % i.title)

def delete(request,items):
    '''
    Permanently delete each member of queryset "items"
    '''
    for i in items:
        messages.success(request, "%s deleted permanently." % i.title)
        i.delete()

### End reusable functions for notifications



@user_passes_test(can_edit_notifications)
def notifications(request,state=None):
    """
    Process or display the index of notifications
    """
    
    if request.method == 'POST':

        # Convert POST array into list, then select matching records as queryset
        selected = request.POST.getlist('notif_list')
        items = Notification.objects.filter(id__in=selected)

        if 'enqueue' in request.POST:
            enqueue(request,items)
            return HttpResponseRedirect(reverse('notifications_queue'))

        elif 'copy' in request.POST:
            copy_to_drafts(request,items)
            return HttpResponseRedirect(reverse('notifications'))

        if 'endraft' in request.POST:
            endraft(request,items)
            return HttpResponseRedirect(reverse('notifications'))

        elif 'trash' in request.POST:
            trash(request,items)
            return HttpResponseRedirect(reverse('notifications_trash'))

        elif 'delete' in request.POST:
            delete(request,items)
            return HttpResponseRedirect(reverse('notifications'))
            
        else:
            pass

        # Redirect to this view so user can't accidentally resubmit with browser Refresh
        return HttpResponseRedirect(reverse('notifications'))


    # If no POST, display list of notifications. Query is refined by URL-passed "state" arg.
    notifications = Notification.objects.filter(author=request.user).order_by('send_date')
    notifications = notifications.filter(state=state)

    return render_to_response('notifications/index.html', locals(), context_instance=RequestContext(request))


@user_passes_test(can_edit_notifications)
def create(request):
    """
    Create a new notification
    """
    
    if request.POST:
        form = NotificationForm(request.POST,user=request.user)

        if form.is_valid():
            item = form.save(commit=False)
            item.title = form.cleaned_data['title']
            item.description = sanitizeHtml(form.cleaned_data['description'])
            item.author = request.user
            item.state = 'draft'
            item.save()
           
            messages.success(request, "Notification draft added.")  
            return HttpResponseRedirect(reverse('notifications'))            
        
    else:
        form = NotificationForm(user=request.user)
    
    return render_to_response('notifications/edit.html', locals(), context_instance=RequestContext(request)) 


@user_passes_test(can_edit_notifications)
def edit(request,notif_id):
    """
    Edit an existing individual notification.
    """

    notification = get_object_or_404(Notification,pk=notif_id)

    if request.POST:
        form = NotificationForm(request.POST, instance=notification,user=request.user)

        if form.is_valid():
            item = form.save(commit=False)
            item.title = form.cleaned_data['title']
            item.description = sanitizeHtml(form.cleaned_data['description'])
            item.author = request.user
            item.state = 'draft'
            item.save()
                        
            # Also move to queue or drafts if that submit button was clicked. 
            # enqueue() and endraft() take lists, not a single item, hence list notation
            if 'enqueue' in request.POST:
                enqueue(request,[notification,])
                return HttpResponseRedirect(reverse('notifications_queue'))

            if 'endraft' in request.POST:
                endraft(request,[notification,])
                return HttpResponseRedirect(reverse('notifications'))

            if 'trash' in request.POST:
                trash(request,[notification,])
                return HttpResponseRedirect(reverse('notifications_trash'))

            
            messages.success(request, "%s was changed." % item.title)


            return HttpResponseRedirect(reverse('notifications'))

    else:
        form = NotificationForm(instance=notification,user=request.user)

    return render_to_response('notifications/edit.html', locals(), context_instance=RequestContext(request))



def display(request,notif_id):
    """
    Display a Delivered notification to current user.
    """

    # dnote = get_object_or_404(Delivered,notification__pk=notif_id)
    dnote = get_object_or_404(Delivered,id=notif_id)
    

    return render_to_response('notifications/display.html', locals(), context_instance=RequestContext(request))



def display_group(request,notif_id):
    """
    Display the master copy of a notification to current user.
    """

    note = get_object_or_404(Notification,pk=notif_id)

    return render_to_response('notifications/display_group.html', locals(), context_instance=RequestContext(request))


@user_passes_test(lambda u: u.is_superuser)
def deliver_pending(request):

    '''
    Find notifications in Queue state and deliver to all recipients. We actually
    do two things here: 1) Created a Delivered record in our own Notifications app,
    so we have a custom record that can be displayed in the widget, which the user
    can check off as completed, etc.; and 2) Deliver a system message via Postman.
    
    The get_members() method on DynamicList aggregates all logical recipients.
    Django-Postman lets us save a Message instance and takes care of delivery.
    This function is never accessed by users - superusers and cron jobs only.
    Superusers can trigger delivery without cron by accessing /notifications/deliver_pending
    '''
    
    notifications = Notification.objects.filter(state='queue')
    
    for n in notifications:
        
        # Find all members associated with this notification's associated dynamic list
        if n.dlist:
            recips = n.dlist.get_members()

        if n.offering:
            recips = n.offering.get_members()
        
        # What if there's both a dlist and an offering? Need a way to combine them here
        
        for r in recips:
            # Create Postman message
            msg = Message() # Instantiate new message on Postman's Message class
            msg.subject = 'New %s on CalCentral: %s' % (n.type, n.title)
            msg.body = n.description
            msg.sender = n.author
            msg.recipient = r
            msg.moderation_status = STATUS_ACCEPTED # a = accepted. Override postman default = all msgs are pending
            msg.notify_users(STATUS_PENDING,is_auto_moderated=True)
            msg.save()
            
            # Create a Deliver instance for each user
            d = Delivered()
            d.notification = n
            d.user = r
            d.completed = False
            d.deliver_date = datetime.datetime.now()
            d.save()
            
            # Move the notification from the queue to the archive
            n.state = 'arch'
            n.save()
    
    # Since this is not a browser view, just need an empty httpresponse
    return HttpResponseRedirect(reverse('notifications'))            
    
    