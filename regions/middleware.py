from regions.models import Region
from django.shortcuts import redirect
from django.conf import settings


class RegionMiddleware(object):

    def process_request(self, request):
        path = request.get_full_path()
        domain = request.META['HTTP_HOST']
        pieces = domain.split('.')
        if pieces[0] == 'www':
            return redirect('http://%s.%s%s' % (Region.objects.first().url, ".".join(pieces[1:]), path))
        if pieces[0] in ['hexxie', 'dev', 'ticketsloth']:
            return redirect('http://%s.%s%s' % (Region.objects.first().url, domain, path))
        try:
            request.region = Region.objects.get(url=pieces[0])
            request.base_url = ".".join(pieces[1:])
            return None
        except Region.DoesNotExist:
            return redirect('http://%s.%s%s' % (Region.objects.first().url, ".".join(pieces[1:]), path))