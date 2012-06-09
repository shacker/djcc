from django.test import TestCase
from django.template.defaultfilters import slugify
from django.contrib.auth.models import User, Group
from django.test.client import Client
from django.core.urlresolvers import reverse
from people.models import Profile
from resources.models import Schedule, Reservation, Resource 
from resources.forms import ReservationForm
import datetime 

class ReservationTests(TestCase):
    
    def setUp(self):

        #create user and add to groups 
        u = User.objects.create_user('jimbob', 'j@bob.com', 'secret')
        g = Group(name='Web Team')
        g.save()
        u.groups.add(g)
        g = Group(name='Radio Students')
        g.save()
        u.groups.add(g)

        # create profile
        self.profile = Profile.objects.create(user=u,salutation=1)

        # create resources 
        self.resource = Resource.objects.create(name='Upper News')
        self.resource2 = Resource.objects.create(name='Lower News')

        # create schedule for this resource and group
        self.schedule = Schedule.objects.create(name="Rooms Schedule")
        self.schedule.resources.add(self.resource)
        self.schedule.resources.add(self.resource2)
        self.schedule.groups.add(g)

        # login
        self.client = Client()
        self.client.login(username='jimbob', password='secret')


        # create reservation for Apr 21-22 8am
        self.res_apr = self.create_reservation(
                        profile=self.profile,
                        resource=self.resource,
                        start_when=datetime.datetime(2009,4,21,8,0,0),
                        end_when=datetime.datetime(2009,4,22,8,0,0),)

        # create reservation for May 1 8am - May 1 Noon
        self.res_may = self.create_reservation(
                        profile=self.profile,
                        resource=self.resource,
                        start_when=datetime.datetime(2009,5,1,8,0,0),
                        end_when=datetime.datetime(2009,5,1,12,0,0),)

    def create_reservation(self, profile, resource, start_when, end_when):
        res = Reservation(
                    profile=profile,
                    resource=resource,
                    start_when=start_when,
                    end_when=end_when)
        res.save()
        return res
    
    def test_validation_begins_during(self):
        """
        test reservation that begins during an existing reservation
        """
        # Apr 21-25 8am
        form = ReservationForm(
                dict(resource=self.resource.id,
                    # start at 8am
                    start_date='2009-4-21',
                    start_time='8:00',
                    # end at 8am following day
                    end_date='2009-4-25',
                    end_time='8:00',
                    summary='this is a summ',))
        # should conflict and not validate
        self.assertEquals(False, form.is_valid())

    def test_validation_ends_during(self):
        """
        test reservation that ends during an existing reservation
        """
        # Apr 19 8am - Apr 21 1pm
        form = ReservationForm(
                dict(
                    resource=self.resource.id,
                    start_date='2009-4-19',
                    start_time='8:00',
                    end_date='2009-4-21',
                    end_time='13:00',
                    summary='this is a summ'))
        # should conflict and not validate
        self.assertEquals(False, form.is_valid())
        
    def test_validation_starts_at_end(self):
        """
        test reservation form that starts at the same time one ends
        """
        # Apr 22 8am - Apr 25 8am
        form = ReservationForm(
                dict(
                    resource=self.resource.id,
                    start_date='2009-4-22',
                    start_time='8:00',
                    end_date='2009-4-25',
                    end_time='8:00',
                    summary='this is for adv web'))
        # should validate
        self.assertEquals(True, form.is_valid())

    def test_validation_short_within(self):
        """
        test reservation form for Apr 21 1pm to Apr 21 3pm
        """
        form = ReservationForm(
                dict(resource=self.resource.id,
                    start_date='2009-4-21',
                    start_time='13:00',
                    end_date='2009-4-21',
                    end_time='15:00',
                    summary='test summary',))

        self.assertEquals(False, form.is_valid())

    def test_validation_overlap(self):
        """
        test reservation form for May 1 Midnight - May 2 Midnight
        """
        form = ReservationForm(
                dict(resource=self.resource.id,
                    start_date='2009-5-1',
                    start_time='0',
                    end_date='2009-5-2',
                    end_time='0',
                    summary='test summary',))

        self.assertEquals(False, form.is_valid())

    def test_post_form_error(self):
        
        data = dict(resource=self.resource.id,
                    start_date='2009-4-25',
                    start_time='0',
                    end_date='2009-4-23',
                    end_time='0',
                    summary='test summary',)

        response = self.client.post(
                        reverse('resources_reservation_edit', 
                                args=[ self.schedule.id, self.res_apr.id]), data)

        self.assertEquals(response.status_code, 200)

        self.assertFormError(
                response, 'form', None, 
                'End date cannot be before start date.')

    def test_basic_edit(self):
        """
        Test editing self.res_apr
        """
          
        data = dict(resource=self.resource.id,
                    start_date='2009-4-22',
                    start_time='0',
                    end_date='2009-4-23',
                    end_time='0',
                    summary='brand new day',)

        response = self.client.post(
                        reverse('resources_reservation_edit', 
                                args=[self.schedule.id, self.res_apr.id]), data)

        self.assertEquals(response.status_code, 302)

        res = Reservation.objects.get(pk=self.res_apr.id)

        self.assertEquals(res.summary, 'brand new day')

        self.assertEquals(
                res.start_when.strftime("%Y-%m-%d"),
                '2009-04-22')

        self.assertEquals(
                res.end_when.strftime("%Y-%m-%d"),
                '2009-04-23')

    def test_schedules_for_user(self):
        """
        Make sure the .for_user manager filter works correctly.
        """
        
        s = Schedule.objects.for_user(self.profile.user)
        self.assertEquals(self.schedule, s[0])

    def test_basic_create(self):
        """
        Create new reservation with resource 2.
        """

        data = dict( resource=self.resource2.id,
                    start_date='2009-4-22',
                    start_time='0',
                    end_date='2009-4-23',
                    end_time='0',
                    summary='abc',)

        response = self.client.post(
                        reverse('resources_reservation_add', 
                                args=[self.schedule.id, self.resource2.id]), data)
        self.assertEquals(response.status_code, 302)
