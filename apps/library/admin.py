from django.contrib import admin
from library.models import StandardFile,MimeType,FileShare

class MimeTypesAdmin(admin.ModelAdmin):
    list_display = ['mimetype','extension',]


class StandardFileAdmin(admin.ModelAdmin):
    list_display = ['__unicode__','title','added_by','added_on']

class FileShareAdmin(admin.ModelAdmin):
    list_display = ['__unicode__','shared_with']

    
admin.site.register(StandardFile,StandardFileAdmin)
admin.site.register(MimeType,MimeTypesAdmin)
admin.site.register(FileShare,FileShareAdmin)