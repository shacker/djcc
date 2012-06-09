from courses.models import *
from django.contrib import admin
from django.contrib.admin import widgets
from django import forms

# Custom Admin Action enables making a complete copy of a course (like a Save As...)
def make_copy(modeladmin, request, queryset):
    for obj in queryset:
        # Make a copy in memory
        # Override the ID so the db can auto_increment -- otherwise we overwrite the original!
        # Update the title of the new object
        n = obj
        n.id = None
        n.title = "NEW COPY OF: " + obj.title 
        n.save()
        request.user.message_set.create(message="Selected courses have been copied. Remember to set their Instructors and Programs!")
make_copy.short_description = "Make copies of selected courses"


class OfferingAdminForm(forms.ModelForm):
    # To get the list of Instructors in the Course admin form to show only active instructors,
    # need to override the form instance, and in that instance, use our custom active_objects model manager.

    instructors = forms.ModelMultipleChoiceField(
        widget = widgets.FilteredSelectMultiple('Instructors',False),
        queryset = Instructor.objects.all(),
        help_text = "")

    students = forms.ModelMultipleChoiceField(
        widget = widgets.FilteredSelectMultiple('Students',False),
        queryset = User.objects.filter(is_active=True),
        help_text = "")
        

                                
                
class OfferingAdmin(admin.ModelAdmin):
    # list_display = ('title',)
    search_fields = ('title','cstring__name')
    actions = [make_copy]
    form = OfferingAdminForm
    raw_id_fields = ('students',)

class MajorAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)    
    
    
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}    

    
class AssignmentAdmin(admin.ModelAdmin):
    raw_id_fields = ('offering',)

class MaterialAdmin(admin.ModelAdmin):
    raw_id_fields = ('offering',)
    list_display = ('__unicode__','offering')
            
  
class ProgramAdminForm(forms.ModelForm):
    # Custom form for Instructors selection in Program
    instructors = forms.ModelMultipleChoiceField(
                widget = widgets.FilteredSelectMultiple('Instructors',False),
                queryset = Instructor.objects.all(),
                help_text = "")  
                
    description = forms.Textarea()

  
class ProgramAdmin(admin.ModelAdmin):
      
    list_display = ('name','prog_majors')
    form = ProgramAdminForm
    
    def prog_majors(self,obj):
        # Custom method (hack) to display a list of M2M relations in a single Admin colum
        str = ''
        for m in obj.majors.all():
            str += m.name + ", "
        return str

class EvalLogAdmin(admin.ModelAdmin):
    raw_id_fields = ('user',)
    list_display = ('__unicode__','sem','offering','q_group')
    list_filter = ['sem', 'offering', 'q_group']
    search_fields = ('user__username','offering__title','q_group__q_group_title',)    

    
class SemesterAdmin(admin.ModelAdmin):
    list_display = ('name', 'current')

class EvalQuestionAdmin(admin.ModelAdmin):
    list_display = ('text','type','q_group', 'semester_added')
    
class EvalResponseAdmin(admin.ModelAdmin):
    list_display = ('id','text_response','numeric_response','q_group','semester')    

class CourseAdminForm(forms.ModelForm):
    # Custom form for Programs selection in Course
    programs = forms.ModelMultipleChoiceField(
                widget = widgets.FilteredSelectMultiple('Programs',False),
                queryset = Program.objects.all(),
                help_text = "")   
                
    majors = forms.ModelMultipleChoiceField(
        widget = widgets.FilteredSelectMultiple('Majors',False),
        queryset = Major.objects.all(),
        help_text = "")                
                
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title','ccn')  
    form = CourseAdminForm
    
class InstructorAdmin(admin.ModelAdmin):
    pass    
     
admin.site.register(Course,CourseAdmin)
admin.site.register(Offering,OfferingAdmin)
admin.site.register(Program,ProgramAdmin)
admin.site.register(Major,MajorAdmin)
admin.site.register(Category,CategoryAdmin)
admin.site.register(Semester,SemesterAdmin)
admin.site.register(Assignment,AssignmentAdmin)
admin.site.register(Material,MaterialAdmin)
admin.site.register(Cstring)
admin.site.register(EvalQGroup)
admin.site.register(EvalLog,EvalLogAdmin)
admin.site.register(EvalQuestion,EvalQuestionAdmin)
admin.site.register(EvalResponse,EvalResponseAdmin)
