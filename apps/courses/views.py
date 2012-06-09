from courses.models import Program, Offering, Semester, Category, Major, Assignment, Material
from people.models import Instructor
from notifications.models import Notification, Delivered
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.contrib import messages
from courses.forms import CourseContactForm
from postman.models import Message, STATUS_PENDING, STATUS_ACCEPTED


def program_home(request):
    """
    Main course listings page
    """

    # First handle course listing selections from programs switcher dropdown
    if request.POST.get('type'):
        return HttpResponseRedirect(reverse('program_sec_courses',
            kwargs={'progslug':request.POST['type'],})) # Redirect after POST

    programs = Program.objects.all()

    return render_to_response(
        'program/index.html',
        locals(),
        context_instance=RequestContext(request)
        )


def program_categories(request):
    """
    Course categories listing
    """

    categories = Category.objects.all().order_by('name')

    return render_to_response(
        'courses/categories.html',
        locals(),
        context_instance=RequestContext(request)
        )


def program_category(request,slug):
    """
    Single category view
    """

    category = get_object_or_404(Category, slug=slug)

    return render_to_response(
        'courses/category.html',
        locals(),
        context_instance=RequestContext(request)
        )

def program_majors(request):
    """
    Listing of majors
    """

    majors = Major.objects.all()

    return render_to_response(
        'courses/majors.html',
        locals(),
        context_instance=RequestContext(request)
        )


def program_major(request,slug):
    """
    Single major view
    """

    major = get_object_or_404(Major, slug=slug)

    return render_to_response(
        'courses/major.html',
        locals(),
        context_instance=RequestContext(request)
        )


def program_sec_courses(request,progslug=False):
    """
    The "Courses" sub-section for a Program of Study, e.g. Business Reporting Courses
    """

    # First handle selections from programs switcher dropdown
    # Redirect after POST
    if request.POST.get('type'):
        program = get_object_or_404(Program, slug=request.POST.get('type'))
        return HttpResponseRedirect(
                    reverse('program_sec_courses',
                            kwargs={'progslug':program.slug,}))

    program = get_object_or_404(Program, slug=progslug)
    programs = Program.objects.all()
    sem = Semester.objects.get(current=True)
    # Get courses that match the current live semester AND are associated with this view's program slug
    offerings = Offering.objects.filter(in_programs__in=(program.id,),semester=sem)

    return render_to_response(
        'program/section-courses.html',
        locals(),
        context_instance=RequestContext(request)
        )


def program_sec_faculty(request,progslug=False):
    """
    The "Faculty" subsection of a Program of Study, e.g. Business Reporting Faculty
    Subdivied into present faculty, lecturers, and previous (inactive) instructors
    """

    program = get_object_or_404(Program, slug=progslug)
    faculty = program.instructors.filter(profile__user__groups__in=(4,),profile__user__is_active=True)
    lecturers = program.instructors.filter(profile__user__groups__in=(5,),profile__user__is_active=True)
    prev_inst = program.instructors.filter(profile__user__is_active=False)

    return render_to_response(
        'program/section-faculty.html',
        locals(),
        context_instance=RequestContext(request)
        )



def offerings_schedule(request,printable=False,sem_id=False):
    """
    Schedule of ALL course offerings - one view handles both calendar and printable view.
    """

    # First handle selections from semester switcher dropdown
    if request.POST.get('sem'):
        sem = get_object_or_404(Semester, pk=request.POST.get('sem'))
        if printable:
            # Redirect to new semester after POST
            return HttpResponseRedirect(
                        reverse(
                            'courses_descriptions_sem',
                            kwargs={'sem_id':sem.pk}))
        else:
            # Redirect to new semester after POST
            return HttpResponseRedirect(
                        reverse(
                            'courses_schedule_sem',
                            kwargs={'sem_id':sem.pk}))

    # Current semester may come through in the URL. If not, default to current semester.
    if sem_id :
        current_sem = get_object_or_404(Semester,pk=sem_id)
    else:
        current_sem = get_object_or_404(Semester,current=True)

    # Complete list of semesters and courses
    semesters = Semester.objects.filter(live=True).order_by('-id')
    offerings = Offering.objects.filter(semester=current_sem)

    # Which template? Calendar style or printable?
    if printable :
        template = 'courses/descriptions.html'
    else :
        template = 'courses/schedule.html'

    no_sidebar = True

    return render_to_response(
        template, 
        locals(), 
        context_instance=RequestContext(request)
        )



def offering_detail(request,course_id):
    """
    Detail info on a particular course offering
    """

    offering = get_object_or_404(Offering, id=course_id)
    
    if request.user.is_authenticated():
        if request.user in offering.students.all():
            scheduled = True
            

    return render_to_response(
        'courses/offering_detail.html', 
        locals(), 
        context_instance=RequestContext(request)
        )
        

def offering_schedule(request,course_id):
    """
    Class schedule for a particular course offering
    """

    offering = get_object_or_404(Offering, id=course_id)

    return render_to_response(
        'courses/offering_schedule.html', 
        locals(), 
        context_instance=RequestContext(request)
        )   
        
        
def offering_announcements(request,course_id):
    """
    Announcements displayed to students in a given course offering
    """

    offering = get_object_or_404(Offering, id=course_id)
    announcements = Notification.objects.filter(offering=offering)

    return render_to_response(
        'courses/offering_announcements.html', 
        locals(), 
        context_instance=RequestContext(request)
        )  
        
        
def offering_library(request,course_id):
    """
    Files shared with a course offering
    """

    offering = get_object_or_404(Offering, id=course_id)


    return render_to_response(
        'courses/offering_library.html', 
        locals(), 
        context_instance=RequestContext(request)
        ) 

def offering_public(request,course_id):
    """
    Course overview as shared to the public
    """

    offering = get_object_or_404(Offering, id=course_id)

    return render_to_response(
        'courses/offering_public.html', 
        locals(), 
        context_instance=RequestContext(request)
        ) 



            

def offering_contact(request,course_id):
    """
    Allows students to make private contact with instructors of a given offering
    """

    offering = get_object_or_404(Offering, id=course_id)
    recips = offering.instructors.all()
    
    if request.method == 'POST': 
        form = CourseContactForm(request.POST) 
        if form.is_valid(): 
            
            for r in recips:
                # Create Postman message
                # Instantiate new message on Postman's Message class
                msg = Message.objects.create(
                    subject = form.cleaned_data['subject'],
                    body = form.cleaned_data['body'],
                    sender = request.user,
                    recipient = r.profile.user,
                    moderation_status = STATUS_ACCEPTED,
                    )
                # Also send corresponding emails
                msg.notify_users(STATUS_PENDING,is_auto_moderated=True)
             
            messages.success(request, "Message sent.")
            return HttpResponseRedirect(reverse('offering_detail',args=[offering.id]))

    else:
        form = CourseContactForm() # An unbound form
    
    return render_to_response(
        'courses/offering_contact.html', 
        locals(), 
        context_instance=RequestContext(request)
        )                        

        
def offering_policies(request,course_id):
    """
    Simple text field display for grading and policies fields on the Offering model.
    """

    offering = get_object_or_404(Offering, id=course_id)

    
    return render_to_response(
        'courses/offering_policies.html', 
        locals(), 
        context_instance=RequestContext(request)
        ) 
        
        
def offering_assignments(request,course_id):
    """
    List of assignments given by instructors to students in a given course offering.
    """

    offering = get_object_or_404(Offering, id=course_id)
    assignments = Assignment.objects.filter(offering=offering)

    
    return render_to_response(
        'courses/offering_assignments.html', 
        locals(), 
        context_instance=RequestContext(request)
        )          
        
        
        
def offering_assignment_detail(request,assign_id):
    """
    Detail view for individual Assignments (popup only)
    """
    assignment = get_object_or_404(Assignment, id=assign_id)
    
    return render_to_response(
        'courses/assignment_pop.html', 
        locals(), 
        context_instance=RequestContext(request)
        ) 

def offering_materials(request,course_id):
    """
    Materials required by particpants in a given offering
    """

    offering = get_object_or_404(Offering, id=course_id)
    materials = Material.objects.filter(offering=offering)

    return render_to_response(
        'courses/offering_materials.html', 
        locals(), 
        context_instance=RequestContext(request)
        ) 
        
def offering_material_detail(request,material_id):
    """
    Detail view for class materials requirements (popup only)
    """
    material = get_object_or_404(Material, id=material_id)
    
    return render_to_response(
        'courses/material_pop.html', 
        locals(), 
        context_instance=RequestContext(request)
        )
        
        
def offering_participants(request,course_id):
    """
    List of students, TAs and instructors associated with a given course offering.
    """

    offering = get_object_or_404(Offering, id=course_id)
    students = offering.students.all()
    instructors = offering.instructors.all()
    
    return render_to_response(
        'courses/offering_participants.html', 
        locals(), 
        context_instance=RequestContext(request)
        )                      

def program_detail(request,program_slug):
    """
    Detail info on a particular program
    """

    program = get_object_or_404(Program, slug=program_slug)
    instructors = program.instructors.filter(profile__user__is_active=True)

    # For use in Programs sidebar
    programs = Program.objects.all()

    return render_to_response(
        'courses/program_detail.html', 
        locals(), 
        context_instance=RequestContext(request)
        )

