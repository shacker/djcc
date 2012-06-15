from django.conf.urls.defaults import *
from shells.models import *
from django.contrib.auth.models import User


urlpatterns = patterns('shells.views',

    # Shell admin system
    url(r'^admin/?$', 'admin_index', name="shells_admin_index"),
    url(r'^admin/shell/(?P<shell_slug>[\w-]+)$', 'admin_shell', name="shells_admin_shell"),
    url(r'^admin/(?P<shell_id>\d+)/newpage/$', 'admin_new_page', name='shells_admin_new_page'),

    url(r'^admin/page/(?P<page_id>\d+)$', 'admin_edit_page', name="shells_admin_page"),
    url(r'^admin/(?P<page_id>\d+)/delete$', 'admin_delete_page', name="admin_delete_page"),

    url(r'^admin/media/page/(?P<page_id>\w+)/media/$', 'admin_new_media', name="shells_admin_new_media"),
    url(r'^admin/media/(?P<media_id>\w+)/edit/$', 'admin_edit_media', name="shells_admin_edit_media"),
    url(r'^admin/media/(?P<media_id>\d+)/delete$', 'admin_delete_media', name="admin_delete_media"),

    url(r'^admin/widget/page/(?P<page_id>\w+)/widget/$', 'admin_new_widget', name="shells_admin_new_widget"),
    url(r'^admin/widget/(?P<widget_id>\w+)/edit/$', 'admin_edit_widget', name="shells_admin_edit_widget"),
    url(r'^admin/widget/(?P<widget_id>\d+)/delete$', 'admin_delete_widget', name="admin_delete_widget"),

    url(r'^admin/palettes/$', 'view_palettes',name='shell_palettes'),

    # View reorder_pages is only called by JQuery for drag/drop page ordering
    url(r'^reorder_pages/$', 'reorder_pages',name="shells_reorder_pages"),
    url(r'^reorder_widgets/$', 'reorder_widgets',name="shells_reorder_widgets"),

    url(r'^(?P<shell_slug>[\w-]+)/?$', 'shell_page',name='shell_home'),
    url(r'^(?P<shell_slug>[\w-]+)/about/$', 'shell_about',name='shell_about'),
    url(r'^(?P<shell_slug>[\w-]+)/(?P<page_slug>[\w-]+)/$', 'shell_page',name='shell_page'),
)

