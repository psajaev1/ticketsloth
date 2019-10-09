import os

from django.core.urlresolvers import reverse_lazy
from django.conf import settings
from django.db import models
from versatileimagefield.placeholder import OnDiscPlaceholderImage

from accounts.models import User
from datetime import datetime
from taggit.managers import TaggableManager
from regions.models import Region
from versatileimagefield.fields import VersatileImageField, OnStoragePlaceholderImage


class Venue(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    user = models.ForeignKey(User, related_name='venue', null=True)
    bio = models.CharField(max_length=2048, blank=True)
    type = models.CharField(max_length=100, blank=True)
    link = models.URLField(blank=True)
    image = VersatileImageField(
        'Image',
        upload_to='images/venues/',
        width_field='width',
        height_field='height',
        blank=True,
        placeholder_image=OnDiscPlaceholderImage(
            path=os.path.join(
                settings.BASE_DIR,
                'static',
                'placeholder_images',
                'placeholder.jpg'
            )
        )
    )
    height = models.PositiveIntegerField(
        'Image Height',
        blank=True,
        null=True
    )
    width = models.PositiveIntegerField(
        'Image Width',
        blank=True,
        null=True
    )
    address = models.CharField(max_length=2048, blank=True)
    city = models.CharField(max_length=128, blank=True)
    state = models.CharField(max_length=128, blank=True)
    region = models.ForeignKey(Region)

    alcohol_available = models.BooleanField(default=False)
    food_available = models.BooleanField(default=False)
    numbered_seats = models.BooleanField(default=False)
    coat_check_available = models.BooleanField(default=False)


    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse_lazy('profile_venue', args=(self.slug,))

    @property
    def full_address(self):
        return ", ".join((self.address, self.city, self.state))

    def upcoming_events(self):
        return self.events.filter(start_time__gte=datetime.now().date())

    def google_maps_uri(self):
        api_key = "AIzaSyCYDsKfRNswFuTYAamB88mIBXwkI1sqTLI"
        if self.address and self.city and self.state:
            return "https://www.google.com/maps/embed/v1/place?key=%s&q=%s,%s+%s" % (api_key, self.address, self.city, self.state)

        return None


class EventManager(models.Manager):

    def upcoming_events(self):
        return self.filter(start_time__gte=datetime.now().date())


class Event(models.Model):
    name = models.CharField(max_length=255, default='')
    bio = models.TextField(blank=True)
    start_time = models.DateTimeField()
    bands = models.CharField(max_length=255, blank=True)
    venue = models.ForeignKey('Venue', null=True, related_name='events')
    user = models.ForeignKey(User)
    image = VersatileImageField(
        'Image',
        upload_to='images/events/',
        width_field='width',
        height_field='height',
        blank=True,
        placeholder_image=OnDiscPlaceholderImage(
            path=os.path.join(
                settings.BASE_DIR,
                'static',
                'placeholder_images',
                'placeholder.jpg'
            )
        )
    )
    height = models.PositiveIntegerField(
        'Image Height',
        blank=True,
        null=True
    )
    width = models.PositiveIntegerField(
        'Image Width',
        blank=True,
        null=True
    )
    region = models.ForeignKey(Region)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    tags = TaggableManager(blank=True)
    objects = EventManager()

    class Meta:
        ordering = ('start_time',)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse_lazy('profile_event', args=(self.pk,))

    def get_bands_display(self):
        if len(self.bands) > 0:
            return self.bands
        return '-'

    def get_cheapest_price(self):
        return self.tickets.all().order_by('-price').first().price
