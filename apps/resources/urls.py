from django.conf.urls.defaults import *
from django.conf import settings
from django.views.generic import simple
from resources import views


urlpatterns = patterns('',

    url(r'^$',
        views.resource_list,
        name="resources_resource_list"),



    url(r'^reservation/(?P<id>\d+)/$', 
        views.reservation_detail,
        name="resources_reservation_detail"),

    url(r'^reservation/byprofile/(?P<profile_id>\d+)/$', 
        views.reservation_list,
        name="resources_reservation_list"),

    url(r'^schedule/(?P<id>\d+)/$',
        views.schedule_detail,
        name="resources_schedule_detail"),

    url(r'^schedule/(?P<schedule_id>\d+)/reserve/(?P<resource_id>\d+)/$',
        views.reservation_add,
        name="resources_reservation_add"),

    url(r'^schedule/(?P<schedule_id>\d+)/reservation/(?P<id>\d+)/edit/$', 
        views.reservation_edit,
        name="resources_reservation_edit"),

    url(r'^schedule/(?P<schedule_id>\d+)/reservation/(?P<id>\d+)/delete/$', 
        views.reservation_delete,
        name="resources_reservation_delete"),

    url(r'^schedule/(?P<schedule_id>\d+)/reservation/delete_confirmed/$', 
        views.reservation_delete_confirmed,
        name="resources_reservation_delete_confirmed"),

)
