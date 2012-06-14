DJCC: Personal experimental Django implementation of a possible CalCentral.
Scot Hacker: shacker at berkeley dot edu

=====
SETUP
=====

For quick-start simplicity, this distro comes with a pre-loaded data
set in sqlite3 format, so there's no need to install a database engine
or db bindings for Python. You'll just need pip and a few depencies
installed via pip.

Also for simplicity: This repo includes a
local_settings.py that will need to be edited to match your setup.
Normally, local_settings.py would not be part of a shared repo and
each user would create their own (it overrides global settings in
settings.py)

# Initial setup (Assuming you're using the included sqlite db):

sudo easy_install pip   # If you don't have pip already
pip install virtualenvwrapper   # If you don't have virtualenv already
mkvirtualenv djcc
workon djcc
cdvirtualenv
git clone https://github.com/shacker/djcc.git
pip install -r requirements.txt
# Modify paths in local_settings.py
cp djcc/manage.py .
python manage.py createsuperuser	# Create a superuser login for yourself

# Daily workflow:

workon djcc
cdvirtualenv
python manage.py runserver

visit: http://127.0.0.1:8000/
visit: http://127.0.0.1:8000/admin

=====

# If you want to use mysql or another db, configure local_settings.py, then
# then import sample data. Something like:

DATABASES = {
     'default': {
         'NAME': 'djcc',
         'ENGINE': 'django.db.backends.mysql',
         'USER': 'shack',
         'PASSWORD': 'foo',
         'HOST': '',
     }
 }


gunzip data/djcc1.json.gz
python manage.py loaddata data/djcc1.json


=====================
MISC NOTES...

Unlike OAE, the Django console should be run in the foreground, not background - it refreshes itself in seconds, and output is always visible.


Make sure mysql is set to create tables and fields as utf8. Running this query after db creation will ensure that all future tables and fields are set correctly by default:
ALTER DATABASE [dbname] CHARACTER SET utf8 COLLATE utf8_general_ci;

In the admin, create groups: students, staff, instructors

Load sample data by running create_users.py

Note: Django has its own "staff" status which just means a user has basic access to the admin. NOT that they can see anything in the admin you haven't OK'd. Not to be confused with them being staff of UCB.

====

To generate a graphical display of the models relationship:

# Create a dot file
$ python manage.py graph_models -a > my_project.dot

# Create a PNG image file called my_project_visualized.png with application grouping
$ python manage.py graph_models -a -g -o my_project_visualized.png

# Create a dot file for only the 'foo' and 'bar' applications of your project
$ python manage.py graph_models foo bar > my_project.dot

Install Graphviz for Mac to view .dot files

====

Some 3rd party template systems (such as jQuery templates) use a template syntax similar to Django's. To prevent these from conflicting, I've installed a templatetag called "verbatim". If you need it, use:

{% load verbatim %}
...
{% verbatim %}
{% endverbatim %}

=====

To start debugging, put this anywhere in your code and reload:

import pdb; pdb.set_trace()

See this for good info on pdb debugging:
http://ericholscher.com/blog/2008/aug/31/using-pdb-python-debugger-django-debugging-series-/

Notes:
use 'l' to list the current function
use 's' for step
use 'r' for return, to go to the end of functions
use "where" for a traceback showing how you got to that place in the code
use 'locals()' to see all local variables
use up + down to see parents and children (unclearl on this)
use keys 'c' or 'n' to continue or go to next.

=====

Export and import a fully working data set, avoiding the contenttypes problem

python manage.py dumpdata --all --indent 4 --ensure_ascii=False > data/all.json
#switch settings to new db, or on a fresh machine
python manage.py syncdb
# Dont create a superuser if the dataset you're about to import already has one
python manage.py reset contenttypes # Needed to avoid import errors
python manage.py loaddata all.json


====

Example API URLs - Note the hierarchical traversal from top level down

See bottom of homepage after logging in for API examples.


