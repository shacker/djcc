from django.test import TestCase
from django.contrib.auth.models import User, Group
from people.models import Staff, Instructor, Student, Alumni, Profile
from people import forms as pforms


def create_user(username):
    user =  User.objects.create_user(username, username+"@mail.com", "secret")
    return user

def create_not_active_user(username):
    user =  User.objects.create_user(
                    username, 
                    username+"@mail.com", 
                    "secret",)
    user.is_active = False
    user.save()
    return user

class PeopleTests(TestCase):

    def setUp(self):

        # jan is staff and not active 
        self.jan_user_not_active = create_not_active_user('jan')
        self.profile_not_active = Profile.objects.create(
                                    user=self.jan_user_not_active)
        self.jan_staff = Staff.objects.create(profile=self.profile_not_active)
        self.jan_user_not_active.groups.add(Group.objects.get(name="Staff"))


        # bill is active staff
        self.bill_user = create_user('bill')
        self.bill_profile = Profile.objects.create(
                                user=self.bill_user, 
                                salutation=1, 
                                mobile_phone1=1231231232)
        self.staff = Staff.objects.create(profile=self.bill_profile)
        self.bill_user.groups.add(Group.objects.get(name="Staff"))

        # sam is Staff and Alumni
        self.sam_user = create_user('sam')
        self.sam_profile = Profile.objects.create(
                                user=self.sam_user,
                                salutation=1, 
                                mobile_phone1=1231231232,)
        self.alumni = Alumni.objects.create(
                                profile = self.sam_profile,
                                medium=1,
                                region=2,
                                revision=0)
        self.sam_profile.user.groups.add(Group.objects.get(name="Alumni"))
        self.staff_2 = Staff.objects.create(profile=self.sam_profile,)
        self.sam_profile.user.groups.add(Group.objects.get(name="Staff"))

        # alex is a student
        self.alex_user = create_user('alex')
        self.alex_profile = Profile.objects.create(
                                user= self.alex_user,
                                salutation=1, 
                                mobile_phone1=1231231232)
        self.student = Student.objects.create(profile=self.alex_profile)
        self.alex_profile.user.groups.add(Group.objects.get(name="Students"))

        # paul is an instructor
        self.paul_user = create_user('paul')
        self.paul_profile = Profile.objects.create(
                                user=self.paul_user, 
                                salutation=1, 
                                mobile_phone1=1231231232)
        self.instructor = Instructor.objects.create(profile=self.paul_profile)
        self.paul_user.groups.add(Group.objects.get(name="Faculty"))

        # mary is just alumni 
        self.mary_user = create_user('mary')
        self.mary_profile = Profile.objects.create(
                                user=self.mary_user, 
                                salutation=1, 
                                mobile_phone1=1231231232)
        self.alumni2 = Alumni.objects.create(
                                profile=self.mary_profile,
                                medium=1,
                                region=2,
                                revision=0)
        self.mary_user.groups.add(Group.objects.get(name="Alumni"))

    def test_query(self):
        self.failUnlessEqual(self.staff,Staff.objects.get(pk=self.staff.pk))
        self.failUnlessEqual(self.student,Student.objects.all()[0])
        self.failUnlessEqual(self.alumni,Alumni.objects.all()[0])
        self.failUnlessEqual(self.instructor,Instructor.objects.all()[0])


    def test_one_to_one_contraint(self):
        """
        Staff, Student and Alumni objects should only extend one profile.  Make
        sure you can't create two.  
        """
        pass

    # might not be necessary
    # def test_form_names(self):
    #     """
    #     Make sure our form names are working. 
    #     """
    #    self.failUnlessEqual( 'StudentForm', self.student.get_form_name())
    #    self.failUnlessEqual( 'StaffForm', self.staff.get_form_name())
    #    self.failUnlessEqual( 'AlumniForm', self.alumni.get_form_name())
    #    self.failUnlessEqual( 'AlumniForm', self.alumni.get_form_name())

    def test_form_classes(self):
        """
        Make sure the correct form class is available for extended profiles.
        """

        Form = getattr(pforms,self.staff.get_form_name())
        f = Form(instance=self.staff)
        self.failUnlessEqual( f.__class__, pforms.StaffForm)

        # test form without instance as well
        Form = getattr(pforms,self.staff.get_form_name())
        f = Form()
        self.failUnlessEqual( f.__class__, pforms.StaffForm)

        Form = getattr(pforms,self.instructor.get_form_name())
        f = Form(instance=self.instructor)
        self.failUnlessEqual( f.__class__, pforms.InstructorForm)

        Form = getattr(pforms,self.student.get_form_name())
        f = Form(instance=self.student)
        self.failUnlessEqual( f.__class__, pforms.StudentForm)

        Form = getattr(pforms,self.alumni.get_form_name())
        f = Form(instance=self.alumni)
        self.failUnlessEqual( f.__class__, pforms.AlumniForm)

    def test_profile_query_managers(self):
        p = self.profile_not_active
        self.failUnlessEqual( 
            p, Profile._default_manager.get(pk=self.profile_not_active.pk))
        self.failUnlessEqual( 
            self.jan_staff, Staff.objects.get(pk=self.jan_staff))
        self.failUnlessEqual( 
            self.jan_staff, Staff.objects.get(pk=self.jan_staff))
        

    def test_profile_instructor(self):
        p = self.instructor.profile
        self.failUnlessEqual( False, p.is_alumni())
        self.failUnlessEqual( False, p.is_student())
        self.failUnlessEqual( False, p.is_staff())
        self.failUnlessEqual( True, p.is_instructor())
        self.failUnlessEqual( True, p.is_affiliated())

    def test_profile_staff(self):
        p = self.staff.profile
        self.failUnlessEqual( False, p.is_instructor())
        self.failUnlessEqual( False, p.is_alumni())
        self.failUnlessEqual( False, p.is_student())
        self.failUnlessEqual( True, p.is_staff())
        self.failUnlessEqual( True, p.is_affiliated())

    def test_profile_student(self):
        p = self.student.profile
        self.failUnlessEqual( False, p.is_instructor())
        self.failUnlessEqual( False, p.is_alumni())
        self.failUnlessEqual( False, p.is_staff())
        self.failUnlessEqual( True, p.is_student())
        self.failUnlessEqual( True, p.is_affiliated())

    def test_update_staff_and_alumni(self):
        """
        Editing a profile that is both staff and alumni should update both
        profiles.
        """
        pass

    def test_alumni_not_affiliated(self):
        pass

    def test_delete_student(self):
        """
        Make sure we can delete student data without affecting other
        profile types.
        """
        self.student.delete()
        self.failUnlessEqual(self.alumni, Alumni.objects.all()[0])
        self.failUnlessEqual(self.staff, Staff.objects.get(pk=self.staff.pk))
        self.failUnlessEqual(self.instructor, Instructor.objects.all()[0])
        self.failUnlessEqual(self.alex_user, 
                             User.objects.get(
                                username=self.alex_user.username))

    def test_profile_staff_and_alumni(self):
        """
        Sam is alumni and staff, he is an affiliate.
        """
        p = self.sam_profile
        self.failUnlessEqual( False, p.is_instructor())
        self.failUnlessEqual( False, p.is_student())
        self.failUnlessEqual( True, p.is_staff())
        self.failUnlessEqual( True, p.is_alumni())
        self.failUnlessEqual( True, p.is_affiliated())
        
    def test_not_active_profile_should_fail(self):
        """
        Make sure all the is_something tests fail for a 
        not active user/profile.
        """
        p = self.profile_not_active
        self.failUnlessEqual( False, p.is_instructor())
        self.failUnlessEqual( False, p.is_staff())
        self.failUnlessEqual( False, p.is_student())
        self.failUnlessEqual( False, p.is_alumni())
        self.failUnlessEqual( False, p.is_affiliated())

    def test_in_group_method(self):
        """
        Check if .in_group() method works as expected.
        """
        p = self.student.profile
        self.failUnlessEqual( True, p.in_group('Students'))
        self.failUnlessEqual( True, p.in_group( 
                                        Group.objects.get(name='Students')))
        self.failUnlessEqual( False, p.in_group('Faculty'))
        self.failUnlessEqual( False, p.in_group(
                                        Group.objects.get(name='Faculty')))

        p = self.alumni2.profile
        self.failUnlessEqual( True, p.in_group('Alumni'))
        self.failUnlessEqual( True, p.in_group(
                                        Group.objects.get(name='Alumni')))
        self.failUnlessEqual( False, p.in_group('Staff'))
        self.failUnlessEqual( False, p.in_group(
                                        Group.objects.get(name='Staff')))


    def test_active_objects_manager(self):
        """
        Make sure Model.active_objects works as expected.
        """
        self.failUnlessEqual( 
            Staff.active_objects.all().count(),
            Staff.objects.filter(profile__user__is_active=True).count())
        self.failUnlessEqual( 
            Instructor.active_objects.all().count(),
            Instructor.objects.filter(profile__user__is_active=True).count())
        self.failUnlessEqual( 
            Alumni.active_objects.all().count(),
            Alumni.objects.filter(profile__user__is_active=True).count())
        self.failUnlessEqual(
            Student.active_objects.all().count(),
            Student.objects.filter(profile__user__is_active=True).count())
