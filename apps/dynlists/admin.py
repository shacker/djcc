from django.contrib import admin
from dynlists.models import DynamicList

# class WorldAdmin(admin.ModelAdmin):
#     # prepopulated_fields = {'slug': ('title',)}
#     raw_id_fields = ('members','created_by')    
    
    
admin.site.register(DynamicList)
