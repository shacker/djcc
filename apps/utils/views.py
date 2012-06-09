from BeautifulSoup import BeautifulSoup, Comment
from urlparse import urljoin
from django.utils import simplejson
import re


def sanitizeHtml(value, base_url=None):
    rjs = r'[\s]*(&#x.{1,7})?'.join(list('javascript:'))
    rvb = r'[\s]*(&#x.{1,7})?'.join(list('vbscript:'))
    re_scripts = re.compile('(%s)|(%s)' % (rjs, rvb), re.IGNORECASE)
    validTags = 'p i em strong b u a h1 h2 h3 blockquote br ul ol li'.split()
    validAttrs = 'href src width height'.split()
    urlAttrs = 'href src'.split() # Attributes which should have a URL
    soup = BeautifulSoup(value)
    for comment in soup.findAll(text=lambda text: isinstance(text, Comment)):
        # Get rid of comments
        comment.extract()
    for tag in soup.findAll(True):
        if tag.name not in validTags:
            tag.hidden = True
        attrs = tag.attrs
        tag.attrs = []
        for attr, val in attrs:
            if attr in validAttrs:
                val = re_scripts.sub('', val) # Remove scripts (vbs & js)
                if attr in urlAttrs:
                    val = urljoin(base_url, val) # Calculate the absolute url
                tag.attrs.append((attr, val))

    return soup.renderContents().decode('utf8')



# We only needed this for jquery autoselect. Prob can be removed.
def json_users(request):
    '''
    Takes query from URL param and returns JSON representation of users 
    whose first or last names start with that string.
    '''
    
    # For opt performance in these standalone util functions, do the imports here rather than above.
    from django.contrib.auth.models import User
    from django.http import HttpResponse
    
    # View only returns if ?query param exists in URL
    string = request.GET.get('query', None)
    
    # Name lookups need to be case insensitive
    if string:
        users = User.objects.filter(first_name__istartswith=string)
        
        to_json = {
            'query':string,
            'suggestions':[unicode(u.get_profile()) for u in users],
            'data':[u.username for u in users]
        }

    else:
        to_json = {}
    
    
    return HttpResponse(simplejson.dumps(to_json), mimetype='application/json')
