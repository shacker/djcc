from django.conf.urls.defaults import *
from notifications import views

urlpatterns = patterns('',

    url(r'^drafts$', 
        views.notifications,
        {'state':'draft'},
        name='notifications'),
        
    url(r'^queue$', 
        views.notifications,
        {'state':'queue'},
        name='notifications_queue'),

    url(r'^archived$', 
        views.notifications,
        {'state':'arch'},
        name='notifications_archived'),
        
    url(r'^trash$', 
        views.notifications,
        {'state':'trash'},
        name='notifications_trash'),        

    url(r'^create$', 
        views.create,
        name='notification_create'),  
        
    url(r'^deliver_pending$', 
        views.deliver_pending,
        name='notification_deliver'),                 
        
    url(r'^edit/(?P<notif_id>\d+)$', 
        views.edit,
        name='notification_edit'),        

    url(r'^display/(?P<notif_id>\d+)$', 
        views.display,
        name='notification_display'),        

    url(r'^display_group/(?P<notif_id>\d+)$', 
        views.display_group,
        name='notification_display_group'),        

)

