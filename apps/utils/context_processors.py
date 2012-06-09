# App-indepedent reusable functions

from news.models import Story

def get_site_section(request):
    '''
    We need to know the current section of the site in order to know
    which sidebar to include. Can also be used for other section-dependent stuff
    in the future.
    '''
    site_section = ''

    if request.path == '/':
        site_section = 'home'

    elif request.path.startswith('/messages/'):
        site_section = 'messages'

    elif request.path.startswith('/news/'):
        site_section = 'news'
        
    elif request.path.startswith('/accounts/'):
        site_section = 'news'        

    elif request.path.startswith('/courses/class/'):
        site_section = 'class'

    elif request.path.startswith('/courses/'):
        site_section = 'courses'

    elif request.path.startswith('/programs/'):
        site_section = 'programs'

    elif request.path.startswith('/notifications/'):
        site_section = 'notifications'

    elif request.path.startswith('/profiles/directory/'):
        site_section = 'directory'

    elif request.path.startswith('/profiles/'):
        site_section = 'profiles'

    elif request.path.startswith('/worlds/'):
        site_section = 'worlds'

    elif request.path.startswith('/dynlists/'):
        site_section = 'dynlists'

    elif request.path.startswith('/scheduler/'):
        site_section = 'scheduler'

    elif request.path.startswith('/library/'):
        site_section = 'library'


    else:
        site_section = 'home'

    return {'site_section': site_section}
    
    

def recent_news(request):
    '''
    List of most recent news, for use in sidebar (global context)
    '''
    
    stories = Story.objects.all()[:5]

    return {'recent_news': stories}    