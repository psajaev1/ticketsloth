import os

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.urlresolvers import reverse_lazy
from twilio.rest import Client
from django.utils.text import slugify
from django.db.models import Avg
from localflavor.us.models import PhoneNumberField
from versatileimagefield.fields import VersatileImageField
from versatileimagefield.placeholder import OnDiscPlaceholderImage
from django.conf import settings


ACCOUNT_SID = "AC2b4d371c80ff1228db75c9c9ff2c9ae5"
AUTH_TOKEN = "6e51e64320c57041464f52a504774cba"


class User(AbstractUser):
    bio = models.TextField(blank=True)
    phone_number = PhoneNumberField(blank=True)
    verification_code = models.CharField(max_length=6, blank=True)
    phone_verified = models.BooleanField(default=False)
    phone_verification_attempts = models.PositiveSmallIntegerField(default=0)
    image = VersatileImageField(
        'Image',
        upload_to='images/users/',
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

    def get_absolute_url(self):
        return reverse_lazy('profile_user', args=(self.pk,))

    def send_verification_code(self):
        phone_number = ''.join(x for x in self.phone_number if x.isdigit())
        client = Client(ACCOUNT_SID, AUTH_TOKEN)
        client.messages.create(to="+1%s" % phone_number, body="Welcome to Listing Exchange! Enter %s to verify your account." % self.verification_code, from_="+12402570723")

    def average_review_score(self):
        return self.reviews.aggregate(Avg('rating'))['rating__avg'] or "No Reviews"

    @classmethod
    def create_placeholder_user(cls, object_name):
        name = slugify(object_name)
        name = name[:25] if len(name) > 25 else name
        name = User.generate_available_username_from_name(name)
        user = User.objects.create_user(username=name)
        user.is_active = False
        user.save()
        return user

    @classmethod
    def generate_available_username_from_name(cls, username):
        try:
            User.objects.get(username=username)
        except User.DoesNotExist:
            return username
        append = 1
        while True:
            test_username = username + str(append)
            try:
                User.objects.get(username=test_username)
                append += 1
            except User.DoesNotExist:
                return test_username
