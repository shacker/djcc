# Assuming you're using the included sqlite db:

sudo easy_install pip   # If you don't have it already
pip install virtualenvwrapper   # If you don't have it already
mkvirtualenv djcc
workon djcc
cdvirtualenv
git clone xxx
pip install -r requirements.txt
cp djcc/manage.py .
python manage.py runserver

visit: http://127.0.0.1:8000/
visit: http://127.0.0.1:8000/admin

If you need an admin login for yourself:
python manage.py createsuperuser



=====================
OLD RANDOM NOTES...


checkout djcc

Create a database. Make sure mysql is set to create tables and fields as utf8. Running this query after db creation will ensure that all future tables and fields are set correctly by default:
ALTER DATABASE [dbname] CHARACTER SET utf8 COLLATE utf8_general_ci;

create groups students, staff, instructors

load sample data by running create_users.py

Unlike OAE, the Django console should be run in the foreground, not background - it refreshes itself in seconds, and output is always visible.


Note: Django has its own "staff" status which just means a user has basic access to the admin. NOT that they can see anything in the admin you haven't OK'd. Not to be confused with them being staff of UCB.

====
To generate a graphical display of the models relationship:

# Create a dot file
$ python manage.py graph_models -a > my_project.dot

# Create a PNG image file called my_project_visualized.png with application grouping
$ python manage.py graph_models -a -g -o my_project_visualized.png

# Create a dot file for only the 'foo' and 'bar' applications of your project
$ python manage.py graph_models foo bar > my_project.dot
====

Some 3rd party template systems (such as jQuery templates) use a template syntax similar to Django's. To prevent these from conflicting, we've installed a templatetag called "verbatim". If you need it, use:

{% load verbatim %}
...
{% verbatim %}
{% endverbatim %}

=====
To start debugging, put this anywhere in your codea and reload:

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

====
export and import fully working data set, avoiding the contenttypes problem

python manage.py dumpdata --all --indent 4 --ensure_ascii=False > all.json
#switch settings to new db, or on a fresh machine
python manage.py syncdb
# Dont create a superuser if the dataset you're about to import already has one
python manage.py reset contenttypes # Needed to avoid import errors
python manage.py loaddata all.json