from django.conf.urls import url
from .views import EventWizard, VenueListView, CreateVenueView, VenueDetailView


event_wizard = EventWizard.as_view(url_name='event_step', done_step_name='finished')

urlpatterns = [
    url(r'^$', VenueListView.as_view(), name="venue_list"),
    url(r'^create/$', CreateVenueView.as_view(), name="create_venue"),
    url(r'^(?P<slug>[\w-]+)/$', VenueDetailView.as_view(), name="profile_venue"),
]
