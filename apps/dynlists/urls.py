from django.conf.urls.defaults import *
from dynlists import views

urlpatterns = patterns('',

    url(r'^edit/(?P<dl_id>[\d]+)/$',
        views.dl_edit,
        name='dynamic_list_edit'),

    url(r'^create/$',
        views.dl_edit,
        name='dynamic_list_create'),

    url(r'^$',
        views.dynamic_list_index,
        name='dynamic_lists'),

)

