import datetime
from django.conf import settings
from django.shortcuts import get_object_or_404, render_to_response
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.http import HttpResponseRedirect, Http404, HttpResponse, HttpResponseForbidden
from middleware import Http403
from people.models import Profile
from resources.models import Schedule, Resource, Room, Kit, Reservation
from resources.forms import ReservationForm

try:
    SPAN_DAYS = settings.RESOURCES_SPAN_DAYS
except:
    SPAN_DAYS = 3

try:
    SPAN_HOURS = settings.RESOURCES_SPAN_HOURS
except:
    SPAN_HOURS = 13

class ScheduleCell(object):
    """
    Provide some API to retrieve times and dates to generate the schedule.

    A schedule cell needs to know if it's reserved or not.

    Takes a Resource object and two datetime objects as params.
    """
    
    def __init__(self, row, begin, end):
        self.begin = begin
        self.end = end
        self.reservation = None
        
        for r in row.reservations:
            if (r.start_when <= begin and r.end_when >= end):
                self.reservation = r
            
class ScheduleRow(object):
    """
    Sets up a row for iterating through in the template.

    Takes a begin (datetime object) and minutes parameters to determines 
    the interval.
    """
    
    def __init__(self, resource, begin, end, minutes=30):
        self.resource = resource
        self.date = begin
        self.begin = begin
        self.end = end
        self.delta = datetime.timedelta(minutes=minutes)

        # Get reservations that exist in this row/time-span and 
        # make it a list so it's cached.
        self.reservations = list(
            resource.reservation_set.in_time_span(begin, end))

    def cells(self):
        cells = []
        begin = self.begin
        end = self.end
        while (begin < end):
            cell_begin = begin
            cell_end = begin + self.delta
            begin = begin + self.delta
            cells.append( ScheduleCell(self, cell_begin, cell_end) )
        return cells

def resource_list(request):
    
    schedules = Schedule.objects.for_user(request.user)

    return render_to_response(
                'resources/resource_list.html',
                locals(),
                context_instance=RequestContext(request))


def schedule_detail(request, id):
    """
    Display a schedule, listed by day, to display what resources are 
    available.
    """
    

    schedule = get_object_or_404(Schedule, pk=id)
    resources = Resource.objects.filter(schedule=schedule).order_by('ordering','name')
    rows = []
    start_date = request.GET.get('start_date', None)

    # try to parse start_date or default to today.
    try:
        args = [int(n) for n in start_date.split('-')]
        args += [8,0,0]
        start_date = datetime.datetime(*args)
    except (ValueError, AttributeError):
        start_date = datetime.datetime.today()
        # set the start_date hour as well
        start_date = start_date.replace(hour=8,minute=0,second=0,microsecond=0)
    
    for i in range(SPAN_DAYS):
        begin = start_date + datetime.timedelta(i)
        end = begin + datetime.timedelta(hours=SPAN_HOURS)
        for r in resources:
            rows.append(ScheduleRow(r, begin, end))

    #reservations = Reservation.objects.filter(
    #                start_when__gte=dates[0],
    #                resource__in=resources)


    context = { 'schedule': schedule,
                'rows':rows,
                'resources': resources,}

    if request.is_ajax():
        return render_to_response(
                'resources/schedule_dates_include.html',
                context,
                context_instance=RequestContext(request))

    return render_to_response(
                'resources/schedule_detail.html',
                context,
                context_instance=RequestContext(request))

def reservation_detail(request, id):
    """
    Display the details related to a reservation and also
    allows edit.
    """

    reservation = get_object_or_404(Reservation, pk=id)

    context = { 'reservation': reservation,}

    return render_to_response(
                'resources/reservation_detail.html',
                context,
                context_instance=RequestContext(request))

def reservation_add(request, schedule_id, resource_id):
    """
    Take a resource id and create a reservation object.
    """
    
    resource = get_object_or_404(Resource, pk=resource_id)
    schedule = get_object_or_404(Schedule, pk=schedule_id)
    start_date = request.GET.get('start_date', None)
    end_date = request.GET.get('start_date', None)    
    profile = request.user.get_profile()

    if not resource.is_available():
        raise Http403, "Sorry, this resource is currently not available for checkout."

    if request.method == 'POST':
        form = ReservationForm(request.POST)
        if form.is_valid():

            reservation = form.save(commit=False)
            reservation.start_when = form.cleaned_data['start_when']
            reservation.end_when = form.cleaned_data['end_when']
            reservation.profile = profile
            reservation.resource = resource
            reservation.save()

            request.user.message_set.create(message="Your reservation was saved.")
            # redirect to the schedule detail on the right start date
            return HttpResponseRedirect(
                        reverse('resources_reservation_edit', 
                                args=[schedule.id, reservation.id] ))

    else:
        # Process GET request
        form = ReservationForm( 
                    initial={'start_date':start_date,
                             'end_date':end_date,                            
                             'schedule':schedule.id,
                             'resource':resource.id, })

    return render_to_response(
                'resources/reservation_add.html',
                locals(),
                context_instance=RequestContext(request))

    
def reservation_list(request, profile_id=None):
    """
    Allow filtering of reservations by different attributes.
    """
    profile = get_object_or_404(Profile, pk=profile_id)
    pass

def reservation_edit(request, schedule_id, id):
    """
    Display the details related to a reservation and also process edits.
    """

    schedule = get_object_or_404(Schedule, pk=schedule_id)
    reservation = get_object_or_404(Reservation, pk=id)

    if request.method == 'POST':
        form = ReservationForm(request.POST, instance=reservation,)
        if form.is_valid():
            form.save()
            request.user.message_set.create(
                    message="Your reservation was updated.")
            return HttpResponseRedirect(
                    reverse('resources_reservation_edit', 
                            args=[schedule.id, reservation.id] ))
    else:
        form = ReservationForm( instance=reservation )


    return render_to_response(
                'resources/reservation_edit.html',
                { 'reservation': reservation, 
                  'form': form,
                  'schedule': schedule,},
                context_instance=RequestContext(request))

def reservation_delete(request, schedule_id, id):

    schedule = get_object_or_404(Schedule, pk=schedule_id)
    reservation = get_object_or_404(Reservation, pk=id)

    if request.user.get_profile() != reservation.profile:
        HttpResponseForbidden("Sorry, you did not make this reservation.")

    if request.method == 'POST':

        reservation.delete()
        request.user.message_set.create(
            message="Your reservation was deleted.")
        request.session['refresh_url'] = reverse(
            'resources_schedule_detail', args=[schedule.id]) + '?start_date=' + reservation.start_when.strftime('%Y-%m-%d')

        return HttpResponseRedirect(
                reverse('resources_reservation_delete_confirmed',
                        args=[schedule.id,]))

    else:
        return render_to_response(
                    'resources/reservation_delete.html',
                    { 'reservation' : reservation,
                      'schedule' : schedule},
                    context_instance=RequestContext(request))
        
def reservation_delete_confirmed(request, schedule_id):

    return render_to_response(
                'resources/reservation_delete_confirmed.html',
                {'refresh_url':request.session['refresh_url']},
                context_instance=RequestContext(request))
