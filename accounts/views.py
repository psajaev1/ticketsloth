from random import randint
from django.core.urlresolvers import reverse_lazy, reverse
from django.http import HttpResponseRedirect
from django.views.generic import CreateView, DetailView, FormView, RedirectView, UpdateView
from braces.views import UserFormKwargsMixin
from twilio.base.exceptions import TwilioRestException

from .forms import SignUpForm, PhoneVerificationForm, ProfileUpdateForm
from .models import User
from django.contrib.auth import authenticate, login
from .mixins import VerifiedUserMixin, TicketSlothLoginRequiredMixin


class SignUpView(CreateView):
    template_name = 'create_form.html'
    form_class = SignUpForm

    def get_success_url(self):
        return reverse('phone_verification')

    def form_valid(self, form):
        user = form.save(commit=False)
        user.verification_code = str(randint(100000, 999999))
        user.save()
        new_user = authenticate(username=form.cleaned_data['username'],
                                password=form.cleaned_data['password1'])
        login(self.request, new_user)
        try:
            user.send_verification_code()
        except TwilioRestException:
            pass
        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        context = super(SignUpView, self).get_context_data(**kwargs)
        context['title'] = "Sign Up"
        return context


class UserProfileView(DetailView):
    template_name = 'profile.html'
    context_object_name = 'account'
    model = User

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated() and request.user.pk == int(self.kwargs.get('pk', None)):
            return HttpResponseRedirect(reverse_lazy('profile'))
        return super(UserProfileView, self).dispatch(request, *args, **kwargs)


class OwnUserProfileView(VerifiedUserMixin, DetailView):
    template_name = 'profile_self.html'
    context_object_name = 'user'
    model = User

    def get_object(self, queryset=None):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super(OwnUserProfileView, self).get_context_data(**kwargs)
        context['purchases'] = self.request.user.purchases.all()
        for purchase in context['purchases']:
            purchase.can_review = purchase.user_can_review(self.request.user)
        context['sales'] = self.request.user.sales.all()
        for sale in context['sales']:
            sale.can_review = sale.user_can_review(self.request.user)
        return context


class PhoneVerificationView(TicketSlothLoginRequiredMixin, UserFormKwargsMixin, FormView):
    form_class = PhoneVerificationForm
    template_name = 'create_form.html'
    success_url = reverse_lazy('profile')

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated() and request.user.phone_verified:
            return HttpResponseRedirect(reverse_lazy('profile'))
        return super(PhoneVerificationView, self).dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        form.save()
        # TODO: Replace with actual welcome email
        self.request.user.email_user("Welcome to Listing Exchange", "Welcome")
        return super(PhoneVerificationView, self).form_valid(form)


class ProfileUpdateView(VerifiedUserMixin, UpdateView):
    model = User
    form_class = ProfileUpdateForm
    template_name = 'create_form.html'

    def get_object(self):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super(ProfileUpdateView, self).get_context_data(**kwargs)
        context['title'] = "Edit Profile"
        return context


class RequestNewVerificationCodeView(TicketSlothLoginRequiredMixin, RedirectView):
    permanent = False
    url = reverse_lazy('phone_verification')

    def get(self, request, *args, **kwargs):
        if request.user.phone_verified is False:
            request.user.verification_code = str(randint(100000, 999999))
            request.user.phone_verification_attempts = 0
            request.user.save()
            try:
                request.user.send_verification_code()
            except TwilioRestException:
                pass
        return super(RequestNewVerificationCodeView, self).get(request, *args, **kwargs)