import os
from django.db import models
from django.conf import settings
from django_permanent.models import PermanentModel
from versatileimagefield.placeholder import OnDiscPlaceholderImage

from accounts.models import User
from events.models import Event
from regions.models import Region
from django.core.urlresolvers import reverse_lazy
from versatileimagefield.fields import VersatileImageField, OnStoragePlaceholderImage
from datetime import timedelta


class Listing(PermanentModel):
    title = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = VersatileImageField(
        'Image',
        upload_to='images/listings/',
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
    event = models.ForeignKey(Event, null=True, default=None, related_name='tickets')
    bands = models.CharField(blank=True, max_length=255)
    venue = models.CharField(blank=True, max_length=255)
    seller = models.ForeignKey(User, related_name="tickets_for_sale")
    ticket_committed = models.IntegerField(default=0)
    ticket_sold = models.IntegerField(default=0)
    ticket_total = models.IntegerField(default=0)
    create_date = models.DateTimeField('Date created', auto_now_add=True)
    region = models.ForeignKey(Region)

    def get_absolute_url(self):
        return reverse_lazy('ticket_view', args=(self.pk,))

    def get_list_title(self):
        return self.title

    def get_band_display(self):
        if self.event:
            return self.event.get_bands_display()
        if self.bands:
            return self.bands
        return '-'

    def has_venue(self):
        return (self.event and self.event.venue) or self.venue

    def get_venue_display(self):
        if self.event and self.event.venue:
            return '@%s' % self.event.venue.name
        if self.venue:
            return '@%s' % self.venue
        return ''

    def list_description(self):
        if self.event:
            return self.event.name
        return self.description

    def available_tickets(self):
        return self.ticket_total - (self.ticket_sold + self.ticket_committed)

    def is_sold_out(self):
        return self.available_tickets() <= 0

    def event_date(self):
        if self.event:
            return self.event.start_time
        return self.create_date + timedelta(days=365)


class Transaction(models.Model):
    POSTED    = 'posted'
    COMMITTED = 'committed'
    COMPLETED = 'completed'
    CANCELLED = 'cancelled'
    STATUS_CHOICES = ((POSTED, 'Request Sent'),
                      (COMMITTED, 'Committed'),
                      (COMPLETED, 'Completed'),
                      (CANCELLED, 'Cancelled'))

    LEGAL_STATUS_UPDATES = {
        POSTED: [CANCELLED, COMMITTED],
        COMMITTED: [COMPLETED, CANCELLED],
        COMPLETED: [],
        CANCELLED: [],
    }

    seller = models.ForeignKey(User, related_name="sales")
    buyer = models.ForeignKey(User, related_name="purchases")
    ticket = models.ForeignKey('Listing', related_name='transactions')
    quantity = models.IntegerField(default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=16, default=POSTED, choices=STATUS_CHOICES)
    create_date = models.DateTimeField('Date created', auto_now_add=True)

    def can_update_status_to(self, status):
        return status in self.LEGAL_STATUS_UPDATES[self.status]

    def cancel(self):
        if self.status == self.POSTED:
            self.delete()
        else:
            self.status = self.CANCELLED
            self.save()

    def update_status(self, new_status):
        if not self.can_update_status_to(new_status):
            return False

        current_status = self.status
        if new_status == Transaction.CANCELLED:
            self.cancel()
            if not self.pk:
                return True

        if new_status == self.COMMITTED:
            quantity = self.quantity
            self.ticket.ticket_committed += quantity
            self.ticket.save()
            self.status = new_status
            self.save()
            return True

        elif current_status == self.COMMITTED:
            quantity = self.quantity

            if new_status == self.COMPLETED:
                self.ticket.ticket_committed -= quantity
                self.ticket.ticket_sold += quantity
                self.ticket.save()
                self.status = new_status
                self.save()
                return True
            elif new_status == self.CANCELLED:
                if self.ticket.ticket_committed < self.quantity:
                    quantity = self.ticket.ticket_total
                self.ticket.ticket_committed -= quantity
                self.ticket.save()
                #already saved above
                return True
        return False

    def user_has_reviewed(self, user):
        return Review.objects.filter(transaction=self, creator=user).count() > 0

    def user_can_review(self, user):
        return self.status == Transaction.COMPLETED and \
               user in [self.seller, self.buyer] and\
               not self.user_has_reviewed(user)


class Review(models.Model):
    RATING_CHOICES = ((0, ':('), (2, ':|'), (3, ':)'))
    target = models.ForeignKey(User, verbose_name="Target", related_name="reviews")
    creator = models.ForeignKey(User, verbose_name="Poster", related_name="authored_reviews")
    transaction = models.ForeignKey(Transaction)
    message = models.CharField(max_length=240, default='')
    rating = models.IntegerField(default=2, choices=RATING_CHOICES)
    created_at = models.DateTimeField('Date created', auto_now_add=True)