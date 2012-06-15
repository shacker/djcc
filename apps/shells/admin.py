from django.contrib import admin
from shells.models import Shell,Page,Palette,Media,Widget
from shells.forms import PageAdminForm
# from tinymce.widgets import TinyMCE


# class ShellAdmin(admin.ModelAdmin):
#     prepopulated_fields = {"slug": ("title",)}

#     # When creating/editing Shells, reverse order on the Project dropdown.
#     def formfield_for_foreignkey(self, db_field, request, **kwargs):
#         if db_field.name == "project":
#             kwargs["queryset"] = Project.objects.all().order_by('-shell')
#             return db_field.formfield(**kwargs)
#         return super(ShellAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)


class MediaAdmin(admin.ModelAdmin):
    list_display = ('title','page','FromShell',)

    def FromShell(self, obj):
        return '%s'%(obj.page.shell)




class MediaInline(admin.StackedInline):
     model = Media
     extra = 1

class PageAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}
    list_display = ('title','navorder','shell')
    list_filter = ['shell']
    search_fields = ['title','shell__title','body',]
    inlines = [MediaInline]
    form = PageAdminForm

    # class Media:
    #     js = ['/admin_media/tinymce/jscripts/tiny_mce/tiny_mce.js', '/media/js/tinymce_kdmc_setup.js',]



class PaletteAdmin(admin.ModelAdmin):
    list_display = ('title','default_pal')



admin.site.register(Shell)
admin.site.register(Media,MediaAdmin)
admin.site.register(Page,PageAdmin)
admin.site.register(Palette,PaletteAdmin)
admin.site.register(Widget)
