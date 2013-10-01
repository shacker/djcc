DJCC: Personal experimental Django implementation of a possible CalCentral.
Scot Hacker: shacker at birdhouse dot org


====================
SETUP AND WORKFLOW
====================

# Initial setup

sudo easy_install pip   # If you don't have pip already
pip install virtualenvwrapper   # If you don't have virtualenv already
mkvirtualenv djcc
workon djcc
cdvirtualenv
git clone https://github.com/shacker/djcc.git
pip install -r requirements.txt

# You'll need a local_settings.py containing the settings specific
# to your machine. Get a starter version at:
https://github.com/shacker/djcc/wiki/Sample-local_settings.py
# Edit that file to match your setup (see below on database options).

Now:
cp djcc/manage.py .

# You can either start with an empty dataset, or use provided sample data.
# Scot can provide sample data (request from shacker@berkeley.edu).
# Place the sample data in djcc/djcc/data/all.json, then create initial tables with:

python manage.py syncdb

# Create a superuser login for yourself if you know there's not going to be one
# in the sample data you'll be loading:

python manage.py createsuperuser

# Now load up the sample data:
python manage.py loaddata djcc/data/all.json

# Daily workflow:

workon djcc
cdvirtualenv
python manage.py runserver

visit: http://127.0.0.1:8000/
visit: http://127.0.0.1:8000/admin

====================
WORKING WITH DATA
====================

Data can be migrated between mysql, postgres, or sqlite (or other dbs supported by Django).
Please do not check your json data into the repo until it's fully anonymous.

Use sqlite if you don't already have a running mysql or postgres installation and want
to make setup as easy as possible. I'm thinking we'll probably settle on postgres.

To export your db-neutral data set, avoiding issues with contenttypes via natural keys:

python manage.py dumpdata --all --natural  > djcc/data/all.json


# If switching to a different db, edit your local_settings.py to reference the new db, then:
python manage.py syncdb

# When it asks, go ahed and create a superuser account yourself, UNLESS you know
# that the dataset you're about to import already has one for you.

# Now reset the contenttypes table, since it's about to recreated with possibly different keys:
python manage.py reset contenttypes

# Now you can safely load the data set into a new db:
python manage.py loaddata djcc/data/all.json

# If you want to use mysql or another db, configure local_settings.py, then
# then import sample data. Something like:


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

See bottom of homepage after logging in for API and "model once" examples.

