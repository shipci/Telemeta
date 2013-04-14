from optparse import make_option
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.core.files.base import ContentFile
from telemeta.models import *
from telemeta.views.item import ItemView
from telemeta.util.unaccent import unaccent
from telemeta.cache import TelemetaCache
import urllib

class Command(BaseCommand):
    args = ""
    help = "Download and import a media item"
    option_list = BaseCommand.option_list + (
            make_option('--all',
                action='store',
                dest='code',
                default='default',
                metavar = '<code>',
                help='recompute analysis on files that have already been analyzed'),
            )

    cache_data = TelemetaCache(settings.TELEMETA_DATA_CACHE_DIR)
    cache_export = TelemetaCache(settings.TELEMETA_EXPORT_CACHE_DIR)

    urls = []

    def handle(self, *args, **options):

        for collection in MediaCollection.objects.filter():
            for item in MediaItem.objects.filter(collection=collection):
                print 'analyzing', collection, '|', item,
                start = time.time()
                item_view = ItemView()
                item_view.item_analyze(item)
                stop = time.time()
                print "(%.2fs)" % (stop - start)
