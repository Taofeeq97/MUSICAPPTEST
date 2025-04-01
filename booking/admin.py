from django.contrib import admin

from booking.models import Booking, Event, Venue, Payment

# Register your models here.

admin.site.register(Booking)
admin.site.register(Event)
admin.site.register(Venue)
admin.site.register(Payment)


