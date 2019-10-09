from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Submit, Field, HTML
from .models import Listing, Review
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse_lazy
from haystack.forms import SearchForm
from datetime import date, timedelta
from django.utils import timezone


class ListingForm(forms.ModelForm):
    title = forms.CharField(label="Title", max_length=255, error_messages={'required': "Please enter a title"})
    description = forms.CharField(label="Listing Description", widget=forms.Textarea, max_length=1000, error_messages={'required': "Please enter a description"})
    price = forms.DecimalField(label="Price", error_messages={'required': "Please enter a value"})
    ticket_total = forms.ChoiceField(choices=((str(x), x) for x in range(1,21)), label="Quantity", error_messages={'required': "Please enter a value"})

    event_select = forms.CharField(label="Select Event", max_length=100, required=False)

    def __init__(self, *args, **kwargs):
        super(ListingForm, self).__init__(*args, **kwargs)
        self.fields['event'].required=False
        self.fields['image'].label = "Image (optional)"
        self.fields['event'].label = "Select Event (optional)"
        self.fields['venue'].label = "Select Venue (optional)"
        self.helper = FormHelper()
        self.helper.form_tag = True
        self.helper.attrs = {'id':'venueForm'}
        self.helper.layout = Layout(
            Fieldset(
                None,
                Field('title', wrapper_class="col-md-12 input", placeholder="Title of your listing"),
                Field('description',wrapper_class="col-md-12 input", placeholder="Describe your listing details"),
                Field('image',wrapper_class="col-md-12 input"),
                Field('price', wrapper_class="col-md-7 input", placeholder="Price per ticket in US dollars"),
                Field('ticket_total', wrapper_class="col-md-5 input", placeholder="Number of tickets"),
                Field('event_select', wrapper_class="col-md-12 input", css_class='event_select'),
                HTML('<div class="col-md-12 text-center"><h4>Can\'t find your event?</h4><h5><a href="%s" target="_blank">Add one here</a>, or you can enter some info below</h5></div>' % reverse_lazy('create_event')),
                Field('venue', wrapper_class="col-md-12 input"),

                Field('event', type="hidden", css_class='event_field'),
                HTML('<div class="col-md-12 margin-1">'),
                Submit('submit', 'Submit',css_class="create-btn"),

                HTML('</div>'),
            )
        )


    class Meta:
        model = Listing
        fields = ('title', 'description', 'price', 'ticket_total', 'event', 'venue', 'image')


class ListingUpdateForm(ListingForm):

    def clean_ticket_total(self):
        ticket_total = self.cleaned_data['ticket_total']

        minimum_tickets = self.instance.ticket_sold + self.instance.ticket_committed
        if int(ticket_total) < minimum_tickets:
            raise ValidationError('Number of tickets must be equal to or greater than the number already sold or committed(%d)' % minimum_tickets)
        return ticket_total


class TicketOfferForm(forms.Form):
    quantity = forms.ChoiceField()

    def __init__(self, available_tickets, *args, **kwargs):
        super(TicketOfferForm, self).__init__(*args, **kwargs)
        self.fields['quantity'].choices=((x, x) for x in range(1,available_tickets+1))
        self.helper = FormHelper()
        self.helper.form_show_labels = False
        self.helper.field_class = 'col-xs-4 commit-to-buy-dropdown'
        self.helper.layout = Layout(
            Field('quantity'),
            Submit('submit', 'Commit to Buy', css_class="commit-btn"),
        )


class ReviewForm(forms.ModelForm):
    message = forms.CharField(widget=forms.Textarea, max_length=140)

    def __init__(self, *args, **kwargs):
        super(ReviewForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                None,
                Field('rating', wrapper_class='col-xs-12'),
                Field('message', wrapper_class='col-xs-12'),
                HTML('<div class="col-xs-12">'),
                Submit('submit', 'Submit', css_class="create-btn"),
                HTML('</div>')
            )
        )
        self.helper.form_show_labels = True
        self.helper.label_class = 'col-xs-2'
        self.helper.field_class = 'col-xs-8'

    class Meta:
        model = Review
        fields = ('rating', 'message')


class InputFilterForm(SearchForm):
    q = forms.CharField(required=False,
                        widget=forms.HiddenInput())
    minimum_price = forms.IntegerField(required=False, widget=forms.HiddenInput())
    maximum_price = forms.IntegerField(required=False, widget=forms.HiddenInput())
    number_of_tickets = forms.ChoiceField(choices=((0, 'Any'), (2, '2+'), (3, '3+'), (4, '4+'), (5, '5+'), (6, '6+')), required=False)
    posted = forms.ChoiceField(choices=((365, 'Any time'), (30, 'Last month'), (7, 'Last week'), (1, 'Today')), required=False)

    def __init__(self, *args, **kwargs):
        super(InputFilterForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.disable_csrf = True
        self.helper.layout = Layout(
            Fieldset(
                None,
                Field('q'),
                Field('minimum_price'),
                Field('maximum_price'),
                Field('number_of_tickets'),
                Field('posted'),
                Submit('submit', 'Filter', css_class="create-btn"),
            )
        )
        self.helper.form_show_labels = True

    def search(self):
        if not self.is_valid():
            return self.no_query_found()
        sqs = self.searchqueryset.auto_query(self.cleaned_data['q'])
        if self.cleaned_data['minimum_price']:
            sqs = sqs.filter(price__gte=self.cleaned_data['minimum_price'])
        if self.cleaned_data['number_of_tickets'] and int(self.cleaned_data['number_of_tickets']) > 0:
            sqs = sqs.filter(ticket_total__gte=self.cleaned_data['number_of_tickets'])
        if self.cleaned_data['maximum_price']:
            sqs = sqs.filter(price__lte=self.cleaned_data['maximum_price'])
        if self.cleaned_data['posted']:
            sqs = sqs.filter(create_date__gte=date.today() - timedelta(days=int(self.cleaned_data['posted'])))
        if self.load_all:
            sqs = sqs.load_all()
        today = timezone.now().date()
        start = timezone.datetime(today.year, today.month, today.day) - timedelta(days=1)
        return sqs.filter(event_date__gt=start).order_by('-create_date')

    def no_query_found(self):
        """
        Determines the behavior when no query was found.

        By default, no results are returned (``EmptySearchQuerySet``).

        Should you want to show all results, override this method in your
        own ``SearchForm`` subclass and do ``return self.searchqueryset.all()``.
        """
        return self.searchqueryset.all()


class CustomSearchForm(SearchForm):
    def search(self):
        if not self.is_valid():
            return self.no_query_found()
        sqs = self.searchqueryset.auto_query(self.cleaned_data['q'])
        if self.load_all:
            sqs = sqs.load_all()
        return sqs

    def no_query_found(self):
        """
        Determines the behavior when no query was found.

        By default, no results are returned (``EmptySearchQuerySet``).

        Should you want to show all results, override this method in your
        own ``SearchForm`` subclass and do ``return self.searchqueryset.all()``.
        """
        return self.searchqueryset.all()