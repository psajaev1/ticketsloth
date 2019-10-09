from .views import WishlistView, WishlistItemDeleteView
from django.conf.urls import url

urlpatterns = [
    url(r'^$', WishlistView.as_view(), name="wishlist"),
    url(r'^(?P<pk>[0-9]+)/remove/$', WishlistItemDeleteView.as_view(), name="wishlist_item_delete"),
]
