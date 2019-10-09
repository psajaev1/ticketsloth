from django.db import models
from accounts.models import User
from taggit.managers import TaggableManager
from django.core.urlresolvers import reverse_lazy
from datetime import datetime


class Band(models.Model):
    name = models.CharField(max_length=24, default='')
    slug = models.SlugField(unique=True)
    user = models.ForeignKey(User, related_name='band', null=True)
    bio = models.CharField(max_length=2048, blank=True)
    image = models.ImageField(upload_to='bands', blank=True)
    tags = TaggableManager(blank=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse_lazy('profile_band', args=(self.slug,))

    def upcoming_events(self):
        return self.events.filter(start_time__gte=datetime.now().date())
