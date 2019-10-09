import os
from datetime import datetime, date, time

from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.core.mail import send_mail
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import HttpResponseRedirect
from django.http import JsonResponse
from django.views.generic import CreateView, DetailView, ListView, UpdateView
from formtools.wizard.views import NamedUrlSessionWizardView

from accounts.mixins import VerifiedUserMixin
from accounts.models import User
from events.forms import CreateVenueForm, EventForm
from regions.mixins import RegionCreateViewMixin, RegionMixin
from ..models import Event


def should_show_venue_form(wizard):
    cleaned_data = wizard.get_cleaned_data_for_step('create_event') or {}
    return not cleaned_data.get('venue', False)


class CreateEventView(VerifiedUserMixin, RegionCreateViewMixin, CreateView):
    template_name = 'create_form.html'
    form_class = EventForm

    def form_valid(self, form):
        event = form.save(commit=False)
        event.user = User.create_placeholder_user(event.name)
        return super(CreateEventView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(CreateEventView, self).get_context_data(**kwargs)
        context['title'] = "Create Event"
        return context


class UpdateEventView(UpdateView):
    template_name = 'create_form.html'
    form_class = EventForm

    def get_queryset(self):
        return Event.objects.filter(user=self.request.user)


class EventListView(RegionMixin, ListView):
    template_name = 'events/event_list.html'
    context_object_name = 'event_list'
    model = Event
    paginate_by = 9

    def get_queryset(self):
        today_min = datetime.combine(date.today(), time.min)
        return Event.objects.filter(start_time__gte=today_min).select_related('venue')

    def get_context_data(self, **kwargs):
        context = super(EventListView, self).get_context_data(**kwargs)
        today_min = datetime.combine(date.today(), time.min)
        context['featured_events'] = Event.objects.filter(region=self.request.region, start_time__gte=today_min).order_by('start_time').select_related('venue')[:2]
        return context


class EventDetailView(RegionMixin, DetailView):
    template_name = 'events/event_detail.html'
    context_object_name = 'event'
    model = Event

    def get_context_data(self, **kwargs):
        context = super(EventDetailView, self).get_context_data(**kwargs)
        all_listings = self.object.tickets.all().select_related('seller')
        paginator = Paginator(all_listings, 8)
        page = self.request.GET.get('page')
        try:
            listings = paginator.page(page)
        except PageNotAnInteger:
            listings = paginator.page(1)
        except EmptyPage:
            listings = paginator.page(paginator.num_pages)
        context['listings'] = listings
        return context


class EventWizard(VerifiedUserMixin, NamedUrlSessionWizardView):
    form_list = (
        ('create_event', EventForm),
        ('create_venue', CreateVenueForm),
    )

    condition_dict = {
        'create_venue': should_show_venue_form,
    }

    template_name = 'events/listing_wizard.html'
    done_step_name = 'finished'
    file_storage = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'tmp'))

    def get_form_initial(self, step):
        if step == 'create_venue':
            event_data = self.storage.get_step_data('create_event') or {}
            venue_name = event_data.get('create_event-venue_select','')
            return {'name': venue_name}
        return super(EventWizard, self).get_form_initial(step)

    def done(self, form_list, form_dict, **kwargs):
        event = form_dict.get('create_event', None)
        event = event.save(commit=False)
        venue = form_dict.get('create_venue', None)
        if venue:
            venue = venue.save(commit=False)
            venue.user = User.create_placeholder_user(venue.name)
            venue.region = self.request.region
            venue.save()
            event.venue = venue
            # TODO Replace with real email addresses
            send_mail('New Venue Created', 'A new venue has been added to the site. You can see it at %s' % venue.get_absolute_url(), 'backend@ticketsite.com',
                ['admin@ticketsite.com'], fail_silently=True)

        event.user = User.create_placeholder_user(event.name)
        event.region = self.request.region
        event.save()
        # TODO Replace Event real email addresses
        send_mail('New Event Created', 'A new event has been added to the site. You can see it at %s' % event.get_absolute_url(), 'backend@ticketsite.com',
            ['admin@ticketsite.com'], fail_silently=True)
        return HttpResponseRedirect(event.get_absolute_url())

def event_json(request):
    events_list = [{'label': event.name, 'desc': event.bio, 'id': event.pk} for event in Event.objects.filter(region=request.region)]
    return JsonResponse(events_list, safe=False)
