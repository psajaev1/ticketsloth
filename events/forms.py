from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Submit, Field, HTML
from django.utils.text import slugify
import itertools
from .models import Event, Venue
from django.core.urlresolvers import reverse_lazy


STATES = (('--', '--'), ('AK', 'Alaska'), ('AL', 'Alabama'), ('AZ', 'Arizona'),
    ('AR', 'Arkansas'), ('CA', 'California'), ('CO', 'Colorado'), ('CT', 'Connecticut'),
    ('DE', 'Delaware'), ('DC', 'District of Columbia'), ('FL', 'Florida'), ('GA', 'Georgia'),
    ('HI', 'Hawaii'), ('ID', 'Idaho'), ('IL', 'Illinois'), ('IN', 'Indiana'),
    ('IA', 'Iowa'), ('KS', 'Kansas'), ('KY', 'Kentucky'), ('LA', 'Louisiana'),
    ('ME', 'Maine'), ('MD', 'Maryland'), ('MA', 'Massachusetts'), ('MI', 'Michigan'),
    ('MN', 'Minnesota'), ('MS', 'Mississippi'), ('MO', 'Missouri'), ('MT', 'Montana'),
    ('NE', 'Nebraska'), ('NV', 'Nevada'), ('NH', 'New Hampshire'), ('NJ', 'New Jersey'),
    ('NM', 'New Mexico'), ('NY', 'New York'), ('NC', 'North Carolina'), ('ND', 'North Dakota'),
    ('OH', 'Ohio'), ('OK', 'Oklahoma'), ('OR', 'Oregon'), ('PA', 'Pennsylvania'),
    ('RI', 'Rhode Island'), ('SC', 'South Carolina'), ('SD', 'South Dakota'), ('TN', 'Tennessee'),
    ('TX', 'Texas'), ('UT', 'Utah'), ('VT', 'Vermont'), ('VA', 'Virginia'),
    ('WA', 'Washington'), ('WV', 'West Virginia'), ('WI', 'Wisconsin'), ('WY', 'Wyoming'))

BUY_OR_SELL = (('False', 'I want to sell tickets'), ('True', 'I want to buy tickets'))


class EventForm(forms.ModelForm):
    name = forms.CharField(label="Name", max_length=255, error_messages={'required': "Please enter a value"})
    bio = forms.CharField(label="Description", widget=forms.Textarea, max_length=2000, required=False)
    start_time = forms.CharField(label="Event Date & Time", max_length=128)
    venue_select = forms.CharField(label="Select Venue", max_length=100)

    def __init__(self, *args, **kwargs):
        super(EventForm, self).__init__(*args, **kwargs)
        self.fields['bands'].required=False
        self.fields['venue'].required=False

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                None,
                Field('name', wrapper_class="col-md-12"),
                Field('bio', wrapper_class="col-md-12"),
                Field('image', wrapper_class="col-md-6"),
                Field('start_time', wrapper_class="col-md-6", css_class='start_time'),
                Field('venue_select', wrapper_class="col-md-6 venue-select", css_class='venue_select'),
                Field('venue', type="hidden", css_class='venue_field'),
                Field('bands', wrapper_class="col-md-6", css_class='band_field'),
                Field('tags', placeholder='Tags', wrapper_class="col-md-12"),
                Submit('submit', 'Submit', css_class="create-btn", wrapper_class="col-md-12"),
            )
        )

        self.helper.label_class = "col-lg-12"
        self.helper.field_class = "col-lg-12"

    def clean_start_time(self):
        if self.cleaned_data['start_time'] == '':
            return None
        return self.cleaned_data['start_time'].replace(' ','T')

    class Meta:
        model = Event
        fields = ('name', 'bio', 'start_time', 'bands', 'venue', 'image', 'tags')


class CreateVenueForm(forms.ModelForm):
    name = forms.CharField(label="Name", max_length=255, error_messages={'required': "Please enter a value"})
    bio = forms.CharField(label="Description", widget=forms.Textarea, max_length=2000, required=False)
    address = forms.CharField(label="Address", max_length=255, required=False)
    city = forms.CharField(label="City", max_length=100, required=False)
    state = forms.ChoiceField(label="State", choices=STATES, required=False)

    def __init__(self, *args, **kwargs):
        super(CreateVenueForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                None,
                HTML('<div class="col-md-12"><h3>Add venue details</h3></div>'),
                Field('name', placeholder='Name'),
                Field('bio', placeholder='Description'),
                Field('image'),
                Field('address', placeholder='Street Address'),
                Field('city', placeholder='City'),
                Field('state', placeholder='State'),
                Submit('submit', 'Submit', css_class="create-btn"),
            )
        )
        self.helper.label_class = "col-lg-12"
        self.helper.field_class = "col-lg-12"

    class Meta:
        model = Venue
        fields = ('name', 'bio', 'address', 'city', 'state', 'image')

    def save(self, commit=True):
        instance = super(CreateVenueForm, self).save(commit=False)

        instance.slug = orig = slugify(instance.name)

        for x in itertools.count(1):
            if not Venue.objects.filter(slug=instance.slug).exists():
                break
            instance.slug = '%s-%d' % (orig, x)

        return super(CreateVenueForm, self).save(commit=commit)