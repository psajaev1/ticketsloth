from django.contrib import admin
from .models import Event, Venue


class VenueAdmin(admin.ModelAdmin):
    list_display = ["name", "address", "city", "state"]

admin.site.register(Venue, VenueAdmin)


class EventAdmin(admin.ModelAdmin):
    list_display = ["name", "start_time", "venue"]

admin.site.register(Event, EventAdmin)
