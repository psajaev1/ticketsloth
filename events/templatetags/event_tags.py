import random
from django.template.defaulttags import register
from ..models import Event


@register.inclusion_tag('events/you_may_also_like.html')
def you_may_also_like(region, count=3):
    events = Event.objects.upcoming_events().filter(region=region)
    num_entities = events.count()
    rand_entities = random.sample(range(num_entities), count)
    random_events = events.filter(pk__in=rand_entities)
    return {'events': random_events}

@register.inclusion_tag('venues/you_may_also_like_venues.html')
def you_may_also_like_venues(region, count=3):
    events = Event.objects.upcoming_events().filter(region=region)
    num_entities = events.count()
    rand_entities = random.sample(range(num_entities), count)
    random_events = events.filter(pk__in=rand_entities)
    return {'events': random_events}