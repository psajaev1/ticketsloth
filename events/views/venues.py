from django.db.models import Count
from django.http import JsonResponse
from django.views.generic import CreateView, DetailView, ListView

from accounts.mixins import VerifiedUserMixin
from accounts.models import User
from events.forms import CreateVenueForm
from regions.mixins import RegionCreateViewMixin, RegionMixin
from ..models import Venue


class CreateVenueView(VerifiedUserMixin, RegionCreateViewMixin, CreateView):
    template_name = 'create_form.html'
    form_class = CreateVenueForm

    def form_valid(self, form):
        venue = form.save(commit=False)
        venue.user = User.create_placeholder_user(venue.name)
        return super(CreateVenueView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(CreateVenueView, self).get_context_data(**kwargs)
        context['title'] = "Create Venue"
        return context



class VenueListView(RegionMixin, ListView):
    template_name = 'venues/all_venue_links.html'
    context_object_name = 'venue_list'
    model = Venue
    paginate_by = 12

    def get_queryset(self):
        queryset = super(VenueListView, self).get_queryset()
        return queryset.annotate(num_events=Count('events')) \
                .order_by('-num_events')


class VenueDetailView(RegionMixin, DetailView):
    template_name = 'venues/venue_details.html'
    context_object_name = 'venue'
    model = Venue


def venue_json(request):
    venues_list = [{'label': venue.name, 'desc': venue.full_address, 'id': venue.pk} for venue in Venue.objects.filter(region=request.region)]
    return JsonResponse(venues_list, safe=False)

