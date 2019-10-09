from django.db import models


class Region(models.Model):
    name = models.CharField(max_length=100)
    url = models.SlugField(max_length=100)
    logo = models.ImageField(upload_to="regions/logos")

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name
