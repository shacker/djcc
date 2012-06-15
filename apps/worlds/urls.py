from django.conf.urls.defaults import *
from worlds import views

urlpatterns = patterns('',
    url(r'^$',
        views.membership_list,
        name='membership_list'),

    url(r'^create/$',
        views.create_world,
        name='create_world'),

    url(r'^(?P<slug>[\w-]+)/$',
        views.world_index,
        name='world_index'),

    url(r'^(?P<world_slug>[\w-]+)/edit/$',
        views.edit_world,
        name='edit_world'),

)

