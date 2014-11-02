from django.contrib import admin
from django.contrib import messages
from notifications.models import Notification, Delivered

class NotificationAdmin(admin.ModelAdmin):
    list_display = ('title','type','author','state','send_date',)
    raw_id_fields = ('author',)
    save_as = True

class DeliveredAdmin(admin.ModelAdmin):
    list_display = ('get_title','user','get_from','deliver_date')
    raw_id_fields = ('user',)

    def get_from(self, obj):
        return '%s'%(obj.notification.author)
    get_from.short_description = 'Author'

    def get_title(self, obj):
        return '%s'%(obj.notification.title)
    get_title.short_description = 'Title'


admin.site.register(Notification,NotificationAdmin)
admin.site.register(Delivered,DeliveredAdmin)
