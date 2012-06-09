from django.conf.urls.defaults import *
from people import views

# URLs dealing with profiles

urlpatterns = patterns('',
    url(r'^directory/$',
        views.profiles_list,
        name='directory'),

    url(r'^(?P<grad_yr>\d+)/$',
        views.profiles_resume_index,
        name='people_profiles_resume_index'),

    url(r'^edit/$',
        views.profile_edit,
        name='people_profile_edit'),

    url(r'^add/(?P<related_model>\w+)/$',
        views.profiles_add_edit_related,
        name='people_profile_add_related'),

    url(r'^edit/(?P<related_model>\w+)/(?P<related_obj_id>\d+)/$',
        views.profiles_add_edit_related,
        name='people_profile_edit_related'),

    url(r'^edit/multi/(?P<related_model>\w+)$',
        views.profile_edit_related_multi,
        name='profile_edit_related_multi'),

    url(r'^delete_related/(?P<related_model>\w+)/(?P<related_obj_id>\d+)$',
        views.profile_delete_related,
        name='profile_delete_related'),

    url(r'^following/$',
        views.following,
        name="following"),

    url(r'^(?P<username>\w+)/$',
        views.profile_detail,
        name='people_profile_detail'),

    url(r'^follow/(?P<username>\w+)/$',
        views.follow,
        name="follow"),

    url(r'^unfollow/(?P<username>\w+)/$',
        views.unfollow,
        name="unfollow"),

)

