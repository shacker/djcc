from django.db import models
from courses import constants
from people.models import Profile,Instructor,Student
from django.contrib.auth.models import User
from resources.models import Room
import datetime

'''
A major (e.g. "Journalism") can be in many categories.
A program ("New Media Journalism") can be in many majors.
A course offering can be in many programs.
'''

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True,null=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __unicode__(self):
      return self.name


class Major(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    categories = models.ManyToManyField(Category,blank=True)

    def __unicode__(self):
      return self.name


class Program(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField()
    description = models.TextField(blank=False)
    instructors = models.ManyToManyField(Instructor) # All instructors who have ever taught in this program
    majors = models.ManyToManyField(Major,blank=True)

    def __unicode__(self):
      return self.name



class Semester(models.Model):
    name = models.CharField(max_length=96)
    current = models.NullBooleanField(unique=True,null=True,help_text="Select &quot;Yes&quot; for the current semester, &quot;Unknown&quot; for all others. Ignore the &quot;No&quot; option. Only one semester may be marked current at a time.")
    ord_by = models.IntegerField(null=True, blank=True)
    live = models.BooleanField(default=False, help_text='When checked, this semester&apos;s schedule will appear on the public site.')

    def __unicode__(self):
        return self.name


class Cstring(models.Model):
    # A course string specific to a department, such as "J-200," but we don't use the leading letter here
    name = models.IntegerField(max_length=6)

    class Meta:
        ordering = ['name']
        verbose_name = "Course String"
        verbose_name_plural = "Course Strings"

    def __unicode__(self):
        return str(self.name) # name is now an integer but you must return a string to the admin here!


class EvalQGroup(models.Model):
    q_group_type = models.IntegerField(choices=constants.QUESTION_SET_TYPE_CHOICES,verbose_name="Question set type")
    q_group_title = models.CharField(max_length=765)
    page_header = models.TextField()
    active = models.BooleanField('Active', default=1)

    def __unicode__(self):
        return self.q_group_title

    class Meta:
        verbose_name_plural = "Evaluation Question Sets"
        verbose_name = "Evaluation Question Set"



class Course(models.Model):
    title = models.CharField(max_length=384)
    ccn = models.IntegerField('CCN',max_length=8,blank=True) # This should be an IntegerField, but we have exceptions
    cstring = models.ForeignKey(Cstring,verbose_name='Course String',help_text="e.g. J-200, but without the J")
    units = models.IntegerField(choices=constants.UNIT_TYPE_CHOICES)
    course_type = models.IntegerField(choices=constants.COURSE_TYPE_CHOICES)
    description = models.TextField()
    restrictions = models.TextField(null=True,blank=True)
    programs = models.ManyToManyField(Program,blank=True)
    majors = models.ManyToManyField(Major,blank=True)

    def __unicode__(self):
      return self.title





class Offering(models.Model):
    '''A particular instance of a Course, held in a given semester'''
    course = models.ForeignKey(Course)
    title = models.CharField(blank=True,null=True,max_length=384,help_text='If present, overrides same field in Course model.')
    semester = models.ForeignKey(Semester)
    instructors = models.ManyToManyField(Instructor)
    students = models.ManyToManyField(User,blank=True)
    sec = models.IntegerField('Section',choices=constants.SECTION_TYPE_CHOICES)
    time = models.CharField(max_length=192)
    location = models.ForeignKey(Room,help_text='If location is mixed, such as &quot;Monday in the Mission, Thursday RM 104&quot; then select Other as location and fill in Other Location field.')
    location_other = models.CharField(blank=True, max_length=100)
    grading = models.TextField(blank=True,null=True)
    policies = models.TextField(blank=True,null=True)
    fee = models.BooleanField(default=False,help_text='Fee required to take this course?')
    enroll_lim = models.IntegerField('Enrollment limit',choices=constants.ENROLLMENT_LIMIT_CHOICES,help_text='Enrollment limit for this course (select nothing if there isn&apos;t one.)',blank=True,null=True)
    description_override = models.TextField(blank=True,null=True,help_text='If present, overrides same field in Course model.')
    restrictions_override = models.TextField(null=True,blank=True,help_text='If present, overrides same field in Course model.')
    eval_group = models.ForeignKey(EvalQGroup,verbose_name='Course evaluation question set',null=True,blank=True,related_name="course_eval_group",
        help_text="Which COURSE evaluations question set should this course be evaluated with at the end of the semester?")
    instr_eval_group = models.ForeignKey(EvalQGroup,verbose_name='Instructor evaluation question set',null=True,blank=True,related_name="instr_eval_group",default=2,
        help_text="Which INSTRUCTOR evaluations question set should this course be evaluated with at the end of the semester?")
    # programs = models.ManyToManyField(Program,blank=True)

    def __unicode__(self):
      return self.title if self.title else self.course.title

    def description(self):
        return self.description_override if self.description_override else self.course.description

    def restrictions(self):
        return self.restrictions_override if self.restrictions_override else self.course.restrictions

    def get_members(self):
        '''
        Obtain all members of this course offering, which includes its instructors and TAs.
        '''

        all_members = set()

        # Designated admins
        for u in self.students.all():
          all_members.add(u.id)

        # additional queries here

        return User.objects.filter(pk__in=all_members)


class Assignment(models.Model):
    '''Assignments given to students in a given course offering'''

    offering = models.ForeignKey(Offering)
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    due_date = models.DateTimeField(blank=True, default=datetime.datetime.now)

    def __unicode__(self):
      return self.title


class Material(models.Model):
    '''Materials students will need during a given course offering'''

    offering = models.ForeignKey(Offering)
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    obtain_at = models.CharField(blank=True, max_length=100)
    url = models.URLField(blank=True,null=True,verify_exists=True)
    cost = models.DecimalField('Approximate Cost',blank=True,null=True,max_digits=8,decimal_places=2)

    def __unicode__(self):
      return self.title


class EvalQuestion(models.Model):
    q_group = models.ForeignKey(EvalQGroup,verbose_name="In question group")
    semester_added = models.ForeignKey(Semester)
    type = models.IntegerField(choices=constants.QUESTION_TYPE_CHOICES)
    order = models.IntegerField(null=True,blank=True,help_text='If blank, position of this question in eval cannot be guaranteed.')
    mothball = models.BooleanField(default=False,help_text='Rather than delete old questions, mothball them instead. That will prevent them from appearing on new evaluations, but wont mess with stats in old reports.')
    text = models.TextField()

    def __unicode__(self):
        return self.text[0:50] + " ..." # Just first 50 chars of question  so we don't blow out picklists where this is represented.

    class Meta:
        verbose_name_plural = "Evaluation Questions"
        verbose_name = "Evaluation Question"


class EvalResponse(models.Model):
    batch = models.IntegerField()
    question = models.ForeignKey(EvalQuestion)
    q_group = models.ForeignKey(EvalQGroup,verbose_name='In question set')
    offering = models.ForeignKey(Offering,verbose_name='Offering',null=True)
    # Following field may look unneccessary but is needed because there are
    # multiple instructors in a course and this particular response could be for any of them.
    instructor = models.ForeignKey(Instructor,null=True,blank=True)
    semester = models.ForeignKey(Semester)
    text_response = models.TextField(blank=True,null=True)
    numeric_response = models.IntegerField(null=True,blank=True)

    # Temporarily removing this - will prob need to rewrite Evaluations anyway
    # def __unicode__(self):
    #     return "%s %s" % (self.id, self.text_response[0:75])

    class Meta:
        verbose_name_plural = "Evaluation Responses"
        verbose_name = "Evaluation Response"


class EvalLog(models.Model):
    """
    Evaluations are anonymous! However we do track which students have done which evaluations, WITHOUT
    attaching actual responses to user IDs. This simple model tracks which profiles have evaluated
    which courses. We don't yet track which students are in which courses so we can't provide a list
    of who still has to do their evaluations - this is as close as we can come for now.
    """

    user = models.ForeignKey(User)
    sem = models.ForeignKey(Semester,verbose_name="Semester")
    offering = models.ForeignKey(Offering,null=True,blank=True)
    q_group = models.ForeignKey(EvalQGroup,null=True,blank=True,verbose_name="Question Group")

    def __unicode__(self):
        return "%s" % (self.user)

    class Meta:
        verbose_name_plural = "Evaluation Logs"
        verbose_name = "Evaluation Log Entry"

