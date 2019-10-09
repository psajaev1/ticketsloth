from django.contrib import admin
from .models import Band


class BandAdmin(admin.ModelAdmin):
    list_display = ["name"]

admin.site.register(Band, BandAdmin)
