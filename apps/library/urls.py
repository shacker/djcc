from django.conf.urls.defaults import *
from library import views

# Redirects
urlpatterns = patterns('django.views.generic.simple',
    # If someone tries to access /library, show them their own
    # ('^$', 'redirect_to', {'url' : '/library/shacker/'}),
)

urlpatterns += patterns('',

    url(r'^show/(?P<file_id>[\d]+)/$',
        views.showfile,
        name='library_showfile'),  

    url(r'^share/(?P<file_id>[\d]+)/$',
        views.sharefile,
        name='library_sharefile'),  


    url(r'^add/ajax_upload/$', 
        views.ajax_upload, 
        name="library_ajax_upload"
        ),
                     
    url(r'^add/$',
        views.add_files,
        name='library_add_files'),

    # Anyone's library    
    url(r'^(?P<user_slug>\w+)/$',
        views.listfiles,
        name='library_listfiles'),
    
)

