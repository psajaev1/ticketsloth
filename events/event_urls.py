from django.conf.urls import url
from .views import EventWizard, EventListView, EventDetailView, UpdateEventView


event_wizard = EventWizard.as_view(url_name='event_step', done_step_name='finished')

urlpatterns = [
    url(r'^$', EventListView.as_view(), name="event_list"),
    url(r'^create/$', event_wizard, name="create_event"),
    url(r'^create/(?P<step>.+)$', event_wizard, name="event_step"),
    url(r'^(?P<pk>[0-9]+)/$', EventDetailView.as_view(), name="profile_event"),
    url(r'^(?P<pk>[0-9]+)/edit/$', UpdateEventView.as_view(), name="edit_event"),
]