# from schedular.models import Schedule
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from courses.models import Offering
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.http import HttpResponse


def scheduler(request):
    """
    Show the current user's schedule of courses
    """

    myclasses = Offering.objects.filter(students__in=(request.user,))

    return render_to_response(
        'scheduler/show.html',
        locals(),
        context_instance=RequestContext(request)
        )



def add_course_to_schedule(request,offering_id):
    '''
    Add the selected course to the current user's schedule.
    This view only invoked via ajax, never directly. 
    We only need to return a 200, not a render_to_response.
    '''

    user = request.user
    offering = get_object_or_404(Offering, id=offering_id)

    if request.method == "POST":
        # Skipping the usual form validation since there's nothing but a button to click
        # and it's harmless to add classes to your own schedule.
        offering.students.add(request.user)
        messages.success(request, "Course added to your <a href='/scheduler'>schedule</a>.")
        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


def remove_course_from_schedule(request,offering_id):
    '''
    Remove the selected course from the current user's schedule
    '''

    user = request.user
    offering = get_object_or_404(Offering, id=offering_id)

    offering.students.remove(request.user)
    messages.success(request, "Course removed from your schedule.")
    return HttpResponseRedirect(reverse('scheduler'))