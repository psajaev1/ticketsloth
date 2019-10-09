# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.views.generic import TemplateView

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from accounts.views import UserProfileView, OwnUserProfileView,\
    PhoneVerificationView, RequestNewVerificationCodeView, ProfileUpdateView
from listings.views import AllReviewsView, OwnerListingView, ListingCreateView,\
    ListingDetailView, ListingUpdateView, TicketSearchView, ListingDeleteView, \
    ReviewUserView, IndexView, transaction_update
from events.views import event_json, venue_json
from allauth.account.views import login
admin.autodiscover()

urlpatterns = [
    url(r'^$', IndexView.as_view(), name="home"),
    url(r'^accounts/login/$', login, name="login"), # login url for things that need it
    url(r'^accounts/', include('allauth.urls')),
    url(r'^verify_phone/$', PhoneVerificationView.as_view(), name="phone_verification"),
    url(r'^verify_phone/new/$', RequestNewVerificationCodeView.as_view(), name="new_verification_code"),
    url(r'^profile/$', OwnUserProfileView.as_view(), name="profile"),
    url(r'^profile/edit/$', ProfileUpdateView.as_view(), name="edit_profile"),
    url(r'^users/(?P<pk>[0-9]+)/$', UserProfileView.as_view(), name="profile_user"),
    url(r'^users/(?P<pk>[0-9]+)/reviews/$', AllReviewsView.as_view(), name="all_reviews_view"),
    url(r'^users/(?P<pk>[0-9]+)/listings/$', OwnerListingView.as_view(), name="owner_list_view"),
    url(r'^events/', include('events.event_urls')),
    url(r'^venues/', include('events.venue_urls')),

    url(r'^listings/$', TicketSearchView.as_view(), name="ticket_list"),
    url(r'^listings/create/$', ListingCreateView.as_view(), name="post"),
    url(r'^listings/(?P<pk>[0-9]+)/$',ListingDetailView.as_view(), name="ticket_view"),
    url(r'^listings/(?P<pk>[0-9]+)/edit/$',ListingUpdateView.as_view(), name="ticket_edit"),
    url(r'^listings/(?P<pk>[0-9]+)/delete/$',ListingDeleteView.as_view(), name="ticket_delete"),

    url(r'^reviews/(?P<transaction_id>[0-9]+)/create/$', ReviewUserView.as_view(), name="create_review"),

    url(r'^list/event/', event_json),
    url(r'^list/venue/', venue_json),

    url(r'^transaction/update/', transaction_update, name='transaction_update'),
    url(r'^wishlist/', include('wishlist.urls')),

    url(r'^messages/', include('postman.urls', namespace='postman', app_name='postman')),

    url(r'^about/$', TemplateView.as_view(template_name='pages/about.html'), name='about'),
    url(r'^faq/$', TemplateView.as_view(template_name='pages/faq.html'), name='faq'),
    url(r'^privacy_policy/$', TemplateView.as_view(template_name='pages/privacy_policy.html'), name='privacy_policy'),
    url(r'^terms_of_user/$', TemplateView.as_view(template_name='pages/terms_of_use.html'), name='terms_of_use'),
    url(r'^contact/$', TemplateView.as_view(template_name='pages/contact.html'), name='contact'),

    url(r'^admin/', include(admin.site.urls)),
    ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) \
     #         + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns

handler404 = 'views.handler404'

