import datetime
from haystack import indexes
from telemeta.models import MediaItem


class MediaItemIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    # title = indexes.CharField(model_attr='title')
    # recorded_from_date = indexes.DateField(model_attr='recorded_from_date')

    def get_model(self):
        return MediaItem

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.all()