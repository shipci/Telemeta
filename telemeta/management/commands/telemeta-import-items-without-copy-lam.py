from optparse import make_option
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.core.files.base import ContentFile
from telemeta.models import *
from telemeta.util.unaccent import unaccent
import os, sys

try:
    from django.utils.text import slugify
except ImportError:
    def slugify(string):
        killed_chars = re.sub('[\(\),]', '', string)
        return re.sub(' ', '_', killed_chars)

def beautify(string):
    return os.path.splitext(string)[0].replace('_',' ')


class Command(BaseCommand):
    help = "import media files from a directory in the media directory into a collection (no file copy)"
    args = "media_dir"

    def handle(self, *args, **options):
        import_dir = os.path.abspath(args[-1])
        media_dir = os.path.normpath(settings.MEDIA_ROOT)
        if not media_dir in import_dir:
            sys.exit('This directory is not in the MEDIA_ROOT directory')     

        for root, dirs, files in os.walk(import_dir):
            for filename in files:
                path = root + os.sep + filename
                path = path[len(media_dir)+1:]
        filename_pre, ext = os.path.splitext(filename)
        if ext == '.wav':
            collection_code = '_'.join(filename_pre.split('_')[:4])
                #filename_pre = slugify(collection_code + '_' + filename_pre)
            collections = MediaCollection.objects.filter(code=collection_code)
            if not collections:
                collection = MediaCollection(code=collection_code, title=collection_code)
                collection.public_access = 'full'
                collection.save()
                print 'collection created: ' + collection_code
            else:
                collection = collections[0]
                print 'using collection: ' + collection.code
                
            items = MediaItem.objects.filter(code=filename_pre)
            if not items:
                item = MediaItem(collection=collection, code=filename_pre)
                print 'item created: ' + item.code
            else:
                item = item[0]
                print 'item already exists: ' + items.code
            
            item.title = filename_pre
            item.file = path
            item.public_access = 'full'
            item.save()
