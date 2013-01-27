from django.contrib import admin
from imagekit.admin import AdminThumbnail
from models import * 

class EventImgAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'admin_thumbnail')
    admin_thumbnail = AdminThumbnail(image_field='large_img')

admin.site.register(Venue)
admin.site.register(VenueOwner)
admin.site.register(EventImage, EventImgAdmin)
admin.site.register(Event)
admin.site.register(AttendingStatus)
admin.site.register(ViewedCalendar)
admin.site.register(InvitedStatus)
admin.site.register(ChosenFew)
admin.site.register(SelectedCal)
admin.site.register(RevealedCal)
admin.site.register(Note)

