from django import forms
from django.utils.translation import ugettext_lazy as _
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Submit, Field, HTML
from braces.forms import UserKwargModelFormMixin
from .models import User
from django.core.urlresolvers import reverse_lazy
from localflavor.us.forms import USPhoneNumberField


class SignUpForm(forms.Form):
    username = forms.CharField()
    email = forms.EmailField()
    phone_number = USPhoneNumberField()

    def __init__(self, *args, **kw):
        super(SignUpForm, self).__init__(*args, **kw)
        self.fields.keyOrder = [
            'username',
            'email',
            'phone_number',
            'password1',
            'password2',
            'confirmation_key']

    def signup(self, request, user):
        user.phone_number = self.cleaned_data['phone_number']
        user.save()


class ProfileUpdateForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ('email', 'phone_number', 'bio', 'image')

    def __init__(self, *args, **kwargs):
        super(ProfileUpdateForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                None,
                Field('email', placeholder='Email'),
                Field('phone_number', placeholder='Phone'),
                Field('image'),
                Field('bio', placeholder='Bio'),
                Field('password1', placeholder='Password'),
                Field('password2', placeholder='Retype Password'),
            ),
            Submit('submit', 'Submit', css_class="create-btn"),
        )

        self.helper.label_class = "col-lg-12"
        self.helper.field_class = "col-lg-12"
    error_messages = {
        'password_mismatch': _("The two password fields didn't match."),
    }
    password1 = forms.CharField(label=_("Password"),
        widget=forms.PasswordInput,
        help_text='Leave blank to keep password unchanged',
        required=False)
    password2 = forms.CharField(label=_("Password confirmation"),
        widget=forms.PasswordInput,
        help_text=_("Enter the same password as above, for verification."),
        required=False)

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                self.error_messages['password_mismatch'],
                code='password_mismatch',
            )
        return password2

    def save(self, commit=True):
        user = super(ProfileUpdateForm, self).save(commit=False)
        phone_number = User.objects.get(pk=user.pk).phone_number

        if self.cleaned_data["password1"] and self.cleaned_data['password1'] != '':
            user.set_password(self.cleaned_data["password1"])
        if self.cleaned_data['phone_number'] != phone_number:
            user.phone_verified = False
            user.phone_verification_attempts = 0
            user.send_verification_code()
        if commit:
            user.save()
        return user


class PhoneVerificationForm(UserKwargModelFormMixin, forms.Form):
    verification_code = forms.CharField()

    def __init__(self, *args, **kwargs):
        super(PhoneVerificationForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                None,
                HTML('<div class="col-md-12">A verification code has been sent to %s.</div>' % self.user.phone_number),
                Field('verification_code', placeholder='Verification Code'),
                HTML('<div class="col-md-12"><a href="%s">Request new verification code</a></div>' % reverse_lazy('new_verification_code')),
                Submit('submit', 'Submit', css_class="create-btn"),
            )
        )
        self.helper.label_class = "col-lg-12"
        self.helper.field_class = "col-lg-12"

    def clean_verification_code(self):
        if self.user.phone_verification_attempts > 2:
            raise forms.ValidationError("You have exceeded the maximum number of attempts. Please request a new code.")

        if self.cleaned_data['verification_code'] != self.user.verification_code:
            self.user.phone_verification_attempts += 1
            self.user.save()
            raise forms.ValidationError("The verification code did not match the code that was sent to you. Please try again.")

    def save(self):
        self.user.phone_verified = True
        self.user.save()


