from django.contrib import admin
from notifications.models import * 

admin.site.register(PostedNotification)
admin.site.register(LastCheckedNotification)
admin.site.register(Notification)
