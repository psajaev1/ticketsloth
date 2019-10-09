import json
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.views.generic import ListView, DeleteView

from events.models import Event
from .models import WishListEntry


class WishlistView(ListView):
    template_name = 'wishlist/wishlist.html'
    context_object_name = 'wishlist_items'

    def get_queryset(self):
        return WishListEntry.objects.filter(user=self.request.user)

    def post(self, request, *args, **kwargs):
        user = request.user
        if user.is_anonymous():
            return JsonResponse({'message': 'You must be logged in to add to a wishlist.'}, status=401)
        json_data = json.loads(request.body)
        event_id = json_data.get('event_id', None)
        if not event_id:
            return JsonResponse({'message': 'No event in request.'}, status=400)
        try:
            event = Event.objects.get(pk=event_id)
            entry, created = WishListEntry.objects.get_or_create(event=event, user=user)
            if created:
                return JsonResponse({'message': '%s added to wishlist.' % event.name}, status=200)
            else:
                return JsonResponse({'message': '%s already in wishlist.' % event.name}, status=200)
        except Event.DoesNotExist:
            return JsonResponse({'message': 'Event does not exist.'}, status=404)


class WishlistItemDeleteView(DeleteView):
    success_url = reverse_lazy('wishlist')

    def get_queryset(self):
        return WishListEntry.objects.filter(user=self.request.user)

    def get(self, request, *args, **kwargs):
        return self.delete(request, *args, **kwargs)
