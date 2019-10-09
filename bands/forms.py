from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Submit, Field, HTML
from .models import Band
from django.utils.text import slugify
import itertools


class CreateBandForm(forms.ModelForm):
    name = forms.CharField(label="Name", max_length=255, error_messages={'required': 'Please enter a value'})
    bio = forms.CharField(label="Bio", widget=forms.Textarea, max_length=2000, required=False)

    def __init__(self, *args, **kwargs):
        super(CreateBandForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                None,
                Field('name', placeholder='Name'),
                Field('bio', placeholder='Bio'),
                Field('tags', placeholder='Tags'),
                HTML('<div></div>'),
                Submit('submit', 'Submit', css_class="create-btn"),

            )
        )

        self.helper.label_class = "col-lg-12"
        self.helper.field_class = "col-lg-12"

    class Meta:
        model = Band
        fields = ('name', 'bio', 'tags')

    def save(self, commit=True):
        instance = super(CreateBandForm, self).save(commit=False)

        instance.slug = orig = slugify(instance.name)

        for x in itertools.count(1):
            if not Band.objects.filter(slug=instance.slug).exists():
                break
            instance.slug = '%s-%d' % (orig, x)

        return super(CreateBandForm, self).save(commit=commit)
