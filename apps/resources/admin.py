from django.db.models import Q
from django.contrib import admin 
from django.contrib.admin import widgets
from django import forms
from django.contrib.auth.models import Group
from resources.models import Resource, Room


class RoomAdmin(admin.ModelAdmin):

    search_fields = ['name','notes']
    list_display = ['name','notes','number','has_screen']

    class Meta:
        model = Room

admin.site.register(Room, RoomAdmin)
