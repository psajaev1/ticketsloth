import datetime
from haystack import indexes
from listings.models import Listing


class ListingIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.EdgeNgramField(document=True, use_template=True, template_name="search/indexes/listings/listing_text.txt")
    seller = indexes.CharField(model_attr='seller')
    create_date = indexes.DateTimeField(model_attr='create_date')
    event_date = indexes.DateTimeField(model_attr='event_date')
    region = indexes.CharField(model_attr='region')
    price = indexes.FloatField(model_attr='price')

    def get_model(self):
        return Listing

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.filter(create_date__lte=datetime.datetime.now())


