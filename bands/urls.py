from django.conf.urls import patterns, include, url
from .views import BandListView, CreateBandView, BandDetailView


urlpatterns = patterns('',
    url(r'^bands/$', BandListView.as_view(), name="band_list"),
    url(r'^bands/create/$', CreateBandView.as_view(), name="create_band"),
    url(r'^bands/(?P<slug>[\w-]+)/$', BandDetailView.as_view(), name="profile_band"),
)