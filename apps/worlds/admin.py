from django.contrib import admin
from worlds.models import World,WorldType

class WorldAdmin(admin.ModelAdmin):
    # prepopulated_fields = {'slug': ('title',)}
    raw_id_fields = ('members','created_by')    
    
    
admin.site.register(WorldType)
admin.site.register(World,WorldAdmin)
