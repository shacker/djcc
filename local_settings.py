# Local Settings
# Use this file to override settings.py.

import os

DEBUG = True
TEMPLATE_DEBUG = DEBUG

# With this on, sorl thumbnail won't fail silently
THUMBNAIL_DEBUG = False

# DATABASES = {
#     'default': {
#         'NAME': 'djcc',
#         'ENGINE': 'django.db.backends.mysql',
#         'USER': 'shack',
#         'PASSWORD': 'foo',
#         'HOST': '',
#     }
# }

DATABASES = {
    'default': {
        'NAME': '/Users/shacker/Sites/virtualenvs/djcc/djcc/data/djcc.sqlite',
        'ENGINE': 'django.db.backends.sqlite3',
    }
}



# Make this unique, and don't share it with anybody.
SECRET_KEY = '530jv{123sdf94wkad;pqwu12-13al;dl@#$@!#82adadfs..45-01883jasodifj23442t:KFJ:DLFkj0u-++@09--`999#$21'

TEMPLATE_DIRS = (
    # os.path.join(os.path.dirname(__file__), 'templates'),
    '/Users/shacker/Sites/virtualenvs/djcc/djcc/templates',
)

# Additional locations of static files
STATICFILES_DIRS = (
    '/Users/shacker/Sites/virtualenvs/djcc/djcc/site_media',
)

# Prevent sending of live email during development. Causes email to be
# written to stdout. Include this in localhost settings only, NOT production.
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
