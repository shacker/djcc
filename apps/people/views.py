import re, os, random
from datetime import datetime
from django.shortcuts import render_to_response
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.shortcuts import get_list_or_404, get_object_or_404
from django.core.paginator import Paginator
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.contrib.auth.decorators import login_required 
from django.contrib.auth.models import User, Group
from django.conf import settings
from django.db.models import Q # For search
from people.models import Student, Instructor, Staff, Alumni, Profile, Address
from people.constants import ADDRESS_TYPE_CHOICES
from people import models as people_models
from people import forms as people_forms
from courses.models import Offering
from django.contrib import messages
from django.contrib.sites.models import Site
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.db.models.loading import get_model



class ProfileException(Exception):
    pass


def profile_detail(request, username):
    """
    Display the person's profile.  
    """

    profile = get_object_or_404(Profile,user__username=username)
    
    # If this person is an instructor we also need the list of classes they teach for their faculty page
    if profile.is_instructor():
        # Do a try/except rather than if/else here in case the instructor doesn't have an instructor profile.
        try:
           courses = profile.instructor.offering_set.all().order_by('-semester')
        except Instructor.DoesNotExist:
           courses = None   

    else:
        courses = None

    # Is current visitor following this user's profile, or vice versa?
    following = is_following(request,profile.user.username)
    following_me = is_following_me(request,profile.user.username)
    
    return render_to_response('people/profile_detail.html', locals(), context_instance=RequestContext(request))



@login_required
def profile_edit(request, template_name="people/profile_edit.html", ):
    """
    Handle users editing their own profiles. 
    """

    profile = request.user.profile

    Form = getattr(people_forms, profile.get_form_name())

    if request.method == "POST":

        form = Form(request.POST, request.FILES, instance=profile)

        if form.is_valid():
            form.save()
            messages.success(request, "Your profile was updated.")
            return HttpResponseRedirect(reverse('people_profile_edit'))
    else:
        form = Form(instance=profile)
        
    return render_to_response( 
       template_name, 
        {'form':form, 'profile':profile},
        context_instance=RequestContext(request),
       )
       

@login_required
def profile_edit_related_multi(request, related_model, obj_id=None):
    """
    Provides abstract ability to show multiple instances of a model 
    related to profile (like awards, publications, addresses), and 
    adds a form to post another.
    """

    profile = request.user.profile
    Model = get_model('people', related_model)
    print Model
    
    form_name = '%sForm' % related_model.title()
    Form = getattr(people_forms,form_name)
    
    itemset = Model.objects.filter(profile=profile)

    if request.method == "POST":

        # Handle either bound or unbound form (add new or edit existing)
        instance = None
        if obj_id:
            instance = get_object_or_404(Model, id=obj_id)
                

        form = Form(request.POST, request.FILES, instance=instance)

        if form.is_valid():
            form = form.save(commit=False) 
            form.profile = profile
            form.save()
            messages.success(request, "Address saved.")
            return HttpResponseRedirect(reverse('people_profile_detail',args=[profile.user.username]))
    else:
        form = Form()
        
    return render_to_response( 
       "people/profile_edit_multi.html",
        locals(),
        context_instance=RequestContext(request),
       )   
       
       

@login_required
def profile_delete_related(request, related_model, related_obj_id):
    """
    Provides ability to delete a record on one of the models related to Profile.
    """

    profile = request.user.profile
    Model = get_model('people', related_model)
    item = Model.objects.get(id=related_obj_id)
    print item.profile
    if item.profile == profile:
        item.delete()

    return HttpResponseRedirect(reverse('people_profile_detail',args=[profile.user.username]))


def profiles_add_edit_related(request, 
                          related_model, 
                          related_obj_id=None,
                          template_name="people/profile_edit_related.html"):
    """
    Requires a related_model string and processes an update or creates
    a new object.
    """

    # OtherWork needs an exception because of camel case
    if related_model == 'otherwork':
        related_model = 'OtherWork'
    else:
        # Capitalize first char
        related_model = related_model.title()

    Model = getattr(people_models, related_model)
    Form = getattr(people_forms, '%sForm' % related_model)
    profile = request.user.profile
    instance = None

    if related_obj_id:
        instance = get_object_or_404(Model, pk=related_obj_id, profile=profile)

    if request.method == "POST":
        form = Form(request.POST, request.FILES, instance=instance)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.profile = profile
            obj.save()
            messages.success(request, "Your profile was updated.")
            return HttpResponseRedirect(reverse('people_profile_edit'))
    else:
        form = Form(instance=instance)
        
    return render_to_response(
       template_name, 
        {'form':form, 'profile':profile, 'related_model':related_model},
        context_instance=RequestContext(request),
       )
       

def alumni_edit(request, template="people/alumni_edit.html"):
    """
    Edit Alumni Data
    """
    pass


def _clean_query_dict(dict):
    """
    Remove empty elements from dict and q since it's not passed
    directly to queryset filter.
    """
    for k,v in dict.items():
        if not v or not v.strip():
            del dict[k]
    try:
        del dict['q']
    except KeyError:
        pass

    try:
        del dict['page']
    except KeyError:
        pass

    return dict

def _get_query_val(dict, key):
    """
    Return None if a key has a empty value in the query dict.
    """
    try:
        if dict[key].strip():
            return dict[key]
    except KeyError:
        pass
        
    return None
    
def _get_explanation(query_params, form):
    """
    Given a set of query parameters return a string explaning what
    the query was about.  Try to resolve field names appropriately.
    """
    
    params = []
    val = ''
    for k,v in query_params.items():
        # resolve choices to descriptive string
        try:
            choices = getattr(form.fields[k], 'choices')
            for tuple in choices:
                if tuple[0] == int(v):
                    val = tuple[1]
        except AttributeError:
            pass
        params.append("%s is %s" % (k,val))
    return ', '.join(params)
        
    
@login_required
def profiles_list(request,template_name="people/directory.html"):

    """
    Browse / search / filter contacts.
    """
    # Construct query params dict
    basic_params = {
        'q': request.GET.get('q',''),
        'alum':request.GET.get('alum',0),
        'inactive':request.GET.get('inactive',0),        
        'type':request.GET.get('type',''),}

    alum_params = {
        'q': request.GET.get('q',''),
        'alumni__j200_inst': request.GET.get('alumni__j200_inst',''),
        'alumni__grad_year': request.GET.get('alumni__grad_year',''),
        'alumni__employer__icontains': request.GET.get('alumni__employer__icontains',''),
        'alumni__medium': request.GET.get('alumni__medium',''),
        'address__city__icontains': request.GET.get('address__city__icontains',''),
        'address__state': request.GET.get('address__state',''),
        'location': request.GET.get('location',''),
        'alumni_search': request.GET.get('alumni_search',None),}

    page = request.GET.get('page',1)

    alumni_search = False
    try: 
        if alum_params['alumni_search']:
            alumni_search = True
    except KeyError:
        pass

    all_search = False

    try: 
        if basic_params['alum']:
            all_search = True
    except KeyError:
        pass
    
    # Include inactive users?    
    try: 
        if basic_params['inactive']:
            inactive_search = True
        else:
            inactive_search = False
    except KeyError:
        pass        
        
    keywords = alum_params['q'] or basic_params['q']
    basic_params = _clean_query_dict(basic_params)
    alum_params = _clean_query_dict(alum_params)

    # if alumni search then look at alumni objects
    if alumni_search:
        contact_list = Profile.alumni_objects.all()

        # process query params
        del alum_params['alumni_search']

        # filter based on params
        contact_list  = contact_list.filter(**alum_params)

    # if not alumni search then search all profiles
    elif all_search:
        contact_list = Profile.active_objects.all()

    # if "inactive" is selected, get ALL profiles
    elif inactive_search :
        contact_list = Profile.objects.all()        
       

    # default is all active users
    else:
        contact_list = Profile.active_objects.all()        

    # if keywords then confine search further
    if keywords:
            
        # Use Q object for 'OR' type query (username, firstname, lastname)
        contact_list = contact_list.filter(
                Q(user__email__icontains=keywords) |
                Q(user__username__icontains=keywords) |
                Q(user__first_name__icontains=keywords) |
                Q(user__last_name__icontains=keywords) 
            )
            
    # filter by type
    if _get_query_val(basic_params, 'type'):

        contact_list = contact_list.filter(
                            user__groups__in=[int(basic_params['type'])],
                        )

    # add keywords back since forms needs it 
    if alumni_search:
        alum_params['q'] = keywords
    else:
        basic_params['q'] = keywords

    alum_form = people_forms.AlumniQueryForm(alum_params)
    basic_form = people_forms.QueryForm(basic_params)


    # always order by last name
    contact_list = contact_list.order_by('user__last_name')
    paginator = Paginator(contact_list, 50) # Number of contacts per page
    paginator = paginator.page(page)
    
    return render_to_response( 
      template_name, locals(), context_instance=RequestContext(request),
    )


    
    
def staff_list(request, template_name="misc/staff.html"):
    """
    Public listing of all staff members
    """
    
    staffers = Staff.active_objects.all().order_by('profile__user__last_name')
    
    return render_to_response( 
      template_name, locals(), context_instance=RequestContext(request),
    )
    
    
def profiles_resume_index(request, grad_yr=0, template_name="students/resume_index.html"):
    """
    Public listing of student resumes (profiles) by year
    """
    # students = Student.objects.filter(grad_year=grad_yr,user__is_active=0)
    students = Student.active_objects.filter(grad_year=grad_yr).order_by('profile__user__last_name')

    return render_to_response( 
      template_name, locals(), context_instance=RequestContext(request),
    )    



# Utility functions for follower relationships
# These two functions are similar and should be consolidated
def is_following(request,target):
    """
    Takes a username as "target" and returns True if the current visitor's
    profile is currently following the target user's profile.
    """
    if not request.user.is_authenticated():
        return False
        
    visitor = request.user.get_profile()
    target = get_object_or_404(Profile,user__username=target)
    if target in visitor.followees.all():
        return True

def is_following_me(request,target):
    """
    Takes a username as "target" and returns True if the target profile
    is currently following the current user.
    """
    if not request.user.is_authenticated():
        return False
        
    visitor = request.user.get_profile()
    target = get_object_or_404(Profile,user__username=target)
    if visitor in target.followees.all():
        return True

# These two functions could be consolidated into one
@login_required
def follow(request,username):
    """
    Let one user follow another.
    """

    follower = get_object_or_404(Profile,user=request.user)
    followee = get_object_or_404(Profile,user__username=username)

    # Is current user already following this list/profile?
    if followee in follower.followees.all():
        messages.info(request, "You were already following %s" % followee)
    else:
        follower.followees.add(followee)
        
        # Only send email if followee has that option enabled in their profile
        if followee.email_on_follow == True:

            site = Site.objects.get(id=1) # Need this for link in email template. 
            recipients = [followee.user.email,]
            email_subject = render_to_string("people/follow/followed-subject.txt", { 'follower': follower, 'followee': followee })                    
            email_body_txt = render_to_string("people/follow/followed-body.txt", { 'follower': follower, 'followee': followee, 'site': site, })        

            msg = EmailMessage(email_subject, email_body_txt, settings.DEFAULT_FROM_EMAIL, recipients)
            msg.send(fail_silently=False)
        
        messages.success(request, "You are now following %s" % followee)
    
    return HttpResponseRedirect(reverse('people_profile_detail',args=[username]))
        

def unfollow(request,username):
    """
    Unfollow a profile
    """
    
    follower = get_object_or_404(Profile,user=request.user)
    followee = get_object_or_404(Profile,user__username=username)
    
    # Is current visitor already following this profile?
        
    if followee in follower.followees.all():
        follower.followees.remove(followee)
        messages.success(request, "You are no longer following %s" % followee)
    else:
        messages.error(request, "You can't unfollow someone you weren't following to begin with!")        
        
    return HttpResponseRedirect(reverse('people_profile_detail',args=[username]))



@login_required
def following(request):
    """
    Show people the requesting user is following.
    """
    follower = request.user.get_profile()
    
    return render_to_response('people/follow/followees.html', locals(), context_instance=RequestContext(request))
