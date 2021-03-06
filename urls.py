from django.conf.urls.defaults import patterns, include, url
from django.views.generic.simple import direct_to_template
from django.conf.urls.static import static
from django.conf import settings
from django.contrib import admin
from django.contrib.auth.views import login, logout
from tastypie.api import Api
from news.feeds import LatestNews
import os, imp
import utils

# API imports
from news.api.resources import StoryResource
from courses.api.resources import CourseResource

v1_api = Api(api_name='v1')
v1_api.register(StoryResource())
v1_api.register(CourseResource())
# End API imports



# Use the Django admin
admin.autodiscover()

urlpatterns = patterns('',

    url(r'^$', 'home.views.home', name="home"),
    url(r'^terms_and_conditions$', 'home.views.check_accepted_terms', name="check_terms"),

    url(r'^accounts/login/$',  login, name="login"),
    url(r'^accounts/logout/$', logout, name="logout"),

    (r'^profiles/', include('people.urls')),
    (r'^messages/', include('postman.urls')),
    (r'^dashboard/', include('dashboard.urls')),
    (r'^news/', include('news.urls')),
    (r'^courses/', include('courses.urls')),
    (r'^programs/', include('courses.program_urls')),
    (r'^worlds/', include('worlds.urls')),
    (r'^dynlists/', include('dynlists.urls')),
    (r'^scheduler/', include('scheduler.urls')),
    (r'^notifications/', include('notifications.urls')),
    (r'^library/', include('library.urls')),
    # (r'^api/', include(cc_api.urls)),
    (r'^api/', include(v1_api.urls)),

    # RSS output for News items
    (r'^feeds/news/$', LatestNews()),

    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),

    # Misc utils
    url(r'^json_users/$',
        utils.views.json_users,
        name='json_users'),

    # Static pages
    url(r'^help/$', direct_to_template, {'template': 'static/help.html'},name='help',),
)



if settings.DEBUG:
    # These values for local dev work only. In production, media URL patterns must be mapped in Apache.
    urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),

        ('^' + settings.MEDIA_URL.strip('/') + r'/(?P<path>postman/.*)$', 'django.views.static.serve',
            {'document_root': os.path.join(imp.find_module('postman')[1], 'medias')}),
    )



