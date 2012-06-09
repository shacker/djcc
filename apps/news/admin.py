from django.contrib import admin
from news.models import Story

class StoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('headline',)}
    list_display = ('headline','pubdate')

admin.site.register(Story,StoryAdmin)