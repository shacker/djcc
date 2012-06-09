from django.conf.urls.defaults import *
from dashboard import views

urlpatterns = patterns('',
    url(r'^$', 
        views.dashboard,
        name='dashboard'),

)

