from braces.views import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse_lazy


class TicketSlothLoginRequiredMixin(LoginRequiredMixin):
    def get_login_url(self):
        return reverse_lazy('account_login')


class VerifiedUserMixin(TicketSlothLoginRequiredMixin):
    """
    View mixin which verifies that the user is authenticated.

    NOTE:
        This should be the left-most mixin of a view, except when
        combined with CsrfExemptMixin - which in that case should
        be the left-most mixin.
    """
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated() and not request.user.phone_verified:
            return HttpResponseRedirect(reverse_lazy('phone_verification'))

        return super(VerifiedUserMixin, self).dispatch(
            request, *args, **kwargs)