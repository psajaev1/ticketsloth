from datetime import datetime, date, time

from django.contrib import messages
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponseForbidden, JsonResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.views.generic import CreateView, ListView, DetailView, UpdateView, DeleteView, TemplateView
from haystack.generic_views import SearchView
from accounts.models import User
from accounts.mixins import VerifiedUserMixin
from accounts.notify import EmailManager
from events.models import Event
from regions.models import Region
from regions.mixins import RegionCreateViewMixin, RegionMixin
from .forms import ListingForm, TicketOfferForm, ListingUpdateForm, ReviewForm, InputFilterForm
from .models import Listing, Transaction, Review


# This is the homepage
class IndexView(TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        context['listing_list'] = Listing.objects.filter(region=self.request.region).order_by('-create_date').select_related('event').select_related('event__venue')[:8]
        today_min = datetime.combine(date.today(), time.min)
        context['events_list'] = Event.objects.filter(region=self.request.region, start_time__gte=today_min).order_by('start_time').select_related('venue')[:2]
        context['regions'] = Region.objects.all()
        return context


class ListingCreateView(VerifiedUserMixin, RegionCreateViewMixin, CreateView):
    template_name = 'create_form.html'
    model = Listing
    form_class = ListingForm

    def form_valid(self, form):
        form.instance.seller = self.request.user
        return_value = super(ListingCreateView, self).form_valid(form)
        form.instance.save()
        return return_value

    def get_context_data(self, **kwargs):
        context = super(ListingCreateView, self).get_context_data(**kwargs)
        context['title'] = "Post Listing"
        return context


class ListingDetailView(RegionMixin, DetailView):
    context_object_name = 'ticket'
    model = Listing

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = TicketOfferForm(data=self.request.POST, available_tickets=self.object.available_tickets())
        if form.is_valid() and int(form.cleaned_data['quantity']) <= self.object.available_tickets():
            Transaction.objects.create(
                seller=self.object.seller,
                buyer=self.request.user,
                ticket=self.object,
                quantity=form.cleaned_data['quantity'],
                status=Transaction.POSTED,
                price=self.object.price
            )
            messages.success(self.request, 'Your ticket request has been sent to the seller successfully.')
            return HttpResponseRedirect(self.object.get_absolute_url())
        else:
            messages.error(self.request, 'There was a problem sending your request please try again.')
            return self.render_to_response(self.get_context_data(form=form))

    def get_template_names(self):
        if self.request.user.is_authenticated() and self.object.seller == self.request.user:
            return ['listings/listing_details_owner_view.html']
        else:
            return ['listings/listing_details.html']

    def get_context_data(self, **kwargs):
        context = super(ListingDetailView, self).get_context_data(**kwargs)
        context['transaction_list'] = self.object.transactions.all()
        context['form'] = TicketOfferForm(available_tickets=self.object.available_tickets())
        return context


class ListingUpdateView(UpdateView):
    template_name = 'create_form.html'
    model = Listing
    form_class = ListingUpdateForm

    def get_queryset(self):
        return Listing.objects.filter(seller=self.request.user)

    def form_valid(self, form):
        return_value = super(ListingUpdateView, self).form_valid(form)
        form.instance.save()
        return return_value


class ListingDeleteView(DeleteView):
    model = Listing

    def get_queryset(self):
        return Listing.objects.filter(seller=self.request.user)

    def get_success_url(self):
        return reverse_lazy('profile')


class OwnerListingView(ListView):
    template_name = 'listings/listing_list_user.html'
    context_object_name = 'ticket_list'
    model = Listing

    def get_queryset(self):
        pk = self.kwargs.get('pk', None)
        return Listing.objects.filter(seller_id=pk)

    def get_context_data(self, **kwargs):
        context = super(OwnerListingView, self).get_context_data(**kwargs)
        context['account'] = User.objects.get(pk=self.kwargs.get('pk'))
        return context


class AllReviewsView(ListView):
    template_name = 'reviews/all_reviews.html'
    context_object_name = 'review_list'

    def get_queryset(self):
        pk = self.kwargs.get('pk', None)
        return Review.objects.filter(target_id=pk)

    def get_context_data(self, **kwargs):
        context = super(AllReviewsView, self).get_context_data(**kwargs)
        context['account'] = get_object_or_404(User, pk=self.kwargs['pk'])
        return context


class ReviewUserView(CreateView):
    template_name = 'reviews/leave_review.html'
    form_class = ReviewForm
    target = None

    def dispatch(self, request, *args, **kwargs):
        self.get_target()
        if not self.transaction.user_can_review(request.user):
            return HttpResponseRedirect(reverse_lazy('profile'))
        return super(ReviewUserView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ReviewUserView, self).get_context_data(**kwargs)
        context['target'] = self.target
        context['transaction'] = self.transaction
        return context

    def form_valid(self, form):
        review = form.save(commit=False)
        review.creator = self.request.user
        review.target = self.target
        review.transaction = self.transaction
        return super(ReviewUserView, self).form_valid(form)

    def get_success_url(self):
        return reverse_lazy('profile')

    def get_target(self):
        self.transaction = Transaction.objects.get(pk=self.kwargs['transaction_id'])
        if self.transaction.seller == self.request.user:
            self.target = self.transaction.buyer
        else:
            self.target = self.transaction.seller


def transaction_update(request):
    response = {}
    if request.method == 'POST':
        transaction = get_object_or_404(Transaction, pk=request.POST['transaction_id'])
        # TODO: Add proper permissions check
        new_status = request.POST.get('update', None)
        is_updated = transaction.update_status(new_status=new_status)

        if is_updated:
            if new_status == Transaction.COMMITTED:
                notif_mgr = EmailManager()
                notif_mgr.notify_transactees(notif_mgr.COMMIT_NOTIFICATION, transaction.pk)

            elif new_status == Transaction.COMPLETED:
                notif_mgr = EmailManager()
                notif_mgr.notify_transactees(notif_mgr.COMPLETE_NOTIFICATION, transaction.pk)

        response['message'] = is_updated
        return JsonResponse(response, safe=False)
    return HttpResponseForbidden


class TicketSearchView(RegionMixin, SearchView):
    form_class = InputFilterForm
    paginate_by = 10
    context_object_name = 'listings'

    def get_context_data(self, **kwargs):
        context = super(TicketSearchView, self).get_context_data(**kwargs)
        return context
