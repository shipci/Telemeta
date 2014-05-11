# -*- coding: utf-8 -*-
# Copyright (C) 2007-2010 Samalyse SARL
# Copyright (C) 2010-2011 Parisson SARL

# This software is a computer program whose purpose is to backup, analyse,
# transcode and stream any audio content with its metadata over a web frontend.

# This software is governed by the CeCILL  license under French law and
# abiding by the rules of distribution of free software.  You can  use,
# modify and/ or redistribute the software under the terms of the CeCILL
# license as circulated by CEA, CNRS and INRIA at the following URL
# "http://www.cecill.info".

# As a counterpart to the access to the source code and  rights to copy,
# modify and redistribute granted by the license, users are provided only
# with a limited warranty  and the software's author,  the holder of the
# economic rights,  and the successive licensors  have only  limited
# liability.

# In this respect, the user's attention is drawn to the risks associated
# with loading,  using,  modifying and/or developing or reproducing the
# software by the user in light of its specific status of free software,
# that may mean  that it is complicated to manipulate,  and  that  also
# therefore means  that it is reserved for developers  and  experienced
# professionals having in-depth computer knowledge. Users are therefore
# encouraged to load and test the software's suitability as regards their
# requirements in conditions enabling the security of their systems and/or
# data to be ensured and,  more generally, to use and operate it in the
# same conditions as regards security.

# The fact that you are presently reading this means that you have had
# knowledge of the CeCILL license and that you accept its terms.
#
# Authors: Olivier Guilyardi <olivier@samalyse.com>
#          David LIPSZYC <davidlipszyc@gmail.com>
#          Guillaume Pellerin <yomguy@parisson.com>

import re, os, random
import mimetypes
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError
from telemeta.models.core import *
from telemeta.models.enum import ContextKeyword
from telemeta.util.unaccent import unaccent_icmp
from telemeta.models.location import LocationRelation, Location
from telemeta.models.system import Revision
from telemeta.models.query import *
from telemeta.models.instrument import *
from telemeta.models.enum import *
from telemeta.models.language import *
from telemeta.models.format import *
from telemeta.util.kdenlive.session import *
from django.db import models
from django.db.models import URLField
from django.conf import settings


# Special code regex of collections for the branch
collection_published_code_regex = getattr(settings, 'COLLECTION_PUBLISHED_CODE_REGEX', '[A-Za-z0-9._-]*')
collection_unpublished_code_regex = getattr(settings, 'COLLECTION_UNPUBLISHED_CODE_REGEX', '[A-Za-z0-9._-]*')

# CREM
#collection_published_code_regex   = 'CNRSMH_E_[0-9]{4}(?:_[0-9]{3}){2}'
#collection_unpublished_code_regex = 'CNRSMH_I_[0-9]{4}_[0-9]{3}'

collection_code_regex = '(?:%s|%s)' % (collection_published_code_regex,
                                       collection_unpublished_code_regex)

item_published_code_regex = getattr(settings, 'ITEM_PUBLISHED_CODE_REGEX', '[A-Za-z0-9._-]*')
item_unpublished_code_regex = getattr(settings, 'ITEM_UNPUBLISHED_CODE_REGEX', '[A-Za-z0-9._-]*')

# CREM
# item_published_code_regex    = collection_published_code_regex + '(?:_[0-9]{2,3}){1,2}'
# item_unpublished_code_regex  = collection_unpublished_code_regex + '_[0-9]{2,3}(?:_[0-9]{2,3}){0,2}'

item_code_regex = '(?:%s|%s)' % (item_published_code_regex, item_unpublished_code_regex)

PUBLIC_ACCESS_CHOICES = (('none', _('none')), ('metadata', _('metadata')),
                         ('mixed', _('mixed')), ('full', _('full')))

ITEM_PUBLIC_ACCESS_CHOICES = (('none', _('none')), ('metadata', _('metadata')),
                         ('full', _('full')))

ITEM_TRANSODING_STATUS = ((0, _('broken')), (1, _('pending')), (2, _('processing')),
                         (3, _('done')), (5, _('ready')))

mimetypes.add_type('video/webm','.webm')

app_name = 'telemeta'


def get_random_hash():
    hash = random.getrandbits(64)
    return "%016x" % hash


class MediaResource(ModelCore):
    "Base class of all media objects"

    def public_access_label(self):
        if self.public_access == 'metadata':
            return _('Metadata only')
        elif self.public_access == 'full':
            return _('Sound and metadata')

        return _('Private data')
    public_access_label.verbose_name = _('public access')

    def set_revision(self, user):
        "Save a media object and add a revision"
        Revision.touch(self, user)

    def get_revision(self):
        return Revision.objects.filter(element_type=self.element_type, element_id=self.id).order_by('-time')[0]

    class Meta:
        abstract = True


class MediaBaseResource(MediaResource):
    "Describe a media base resource"

    title                 = CharField(_('title'), required=True)
    description           = CharField(_('description_old'))
    descriptions          = TextField(_('description'))
    code                  = CharField(_('code'), unique=True, required=True)
    public_access         = CharField(_('public access'), choices=PUBLIC_ACCESS_CHOICES,
                                      max_length=16, default="metadata")

    def __unicode__(self):
        return self.code

    @property
    def public_id(self):
        return self.code

    def save(self, force_insert=False, force_update=False, user=None, code=None):
        super(MediaBaseResource, self).save(force_insert, force_update)

    def get_fields(self):
        return self._meta.fields

    class Meta(MetaCore):
        abstract = True
        ordering = ['code']


class MediaRelated(MediaResource):
    "Related media"

    element_type = 'media'

    title           = CharField(_('title'))
    date            = DateTimeField(_('date'), auto_now=True)
    description     = TextField(_('description'))
    mime_type       = CharField(_('mime_type'), null=True)
    url             = CharField(_('url'), max_length=500)
    credits         = CharField(_('credits'))
    file            = FileField(_('file'), upload_to='items/%Y/%m/%d',
                                db_column="filename", max_length=255)

    def is_image(self):
        is_url_image = False
        if self.url:
            url_types = ['.png', '.jpg', '.gif', '.jpeg']
            for type in url_types:
                if type in self.url or type.upper() in self.url:
                    is_url_image = True
        return 'image' in self.mime_type or is_url_image

    def save(self, force_insert=False, force_update=False, author=None):
        super(MediaRelated, self).save(force_insert, force_update)

    def set_mime_type(self):
        if self.file:
            self.mime_type = mimetypes.guess_type(self.file.path)[0]

    def is_kdenlive_session(self):
        if self.file:
            return '.kdenlive' in self.file.path
        else:
            return False

    def __unicode__(self):
        if self.title and not re.match('^ *N *$', self.title):
            title = self.title
        else:
            title = unicode(self.item)
        return title

    class Meta:
        abstract = True


class MediaCollection(MediaResource):
    "Describe a collection of items"

    element_type = 'collection'

    def is_valid_collection_code(value):
        "Check if the collection code is well formed"
        regex = '^' + collection_code_regex + '$'
        if not re.match(regex, value):
            raise ValidationError(u'%s is not a valid collection code' % value)

    # General informations
    reference             = CharField(_('reference'), unique=True, null=True)
    title                 = CharField(_('title'), required=True)
    alt_title             = CharField(_('original title / translation'))
    creator               = CharField(_('depositor / contributor'))
    recording_context     = WeakForeignKey('RecordingContext', related_name="collections",
                                           verbose_name=_('recording context'))
    recorded_from_year    = IntegerField(_('recording year (from)'))
    recorded_to_year      = IntegerField(_('recording year (until)'))
    year_published        = IntegerField(_('year published'))

    # Geographic and cultural informations
    ## See "countries" and "ethnic_groups" methods below

    # Legal notices
    collector             = CharField(_('recordist'))
    publisher             = WeakForeignKey('Publisher', related_name="collections",
                                           verbose_name=_('publisher / status'))
    publisher_collection  = WeakForeignKey('PublisherCollection', related_name="collections",
                                            verbose_name=_('publisher collection'))
    publisher_serial      = CharField(_('publisher serial number'))
    booklet_author        = CharField(_('author of published notice'))
    external_references   = TextField(_('bibliographic references'))
    doctype_code          = IntegerField(_('document type'))
    public_access         = CharField(_('access status'), choices=PUBLIC_ACCESS_CHOICES,
                                      max_length=16, default="metadata")
    auto_period_access    = BooleanField(_('automatic access after a rolling period'), default=True)
    legal_rights          = WeakForeignKey('LegalRight', related_name="collections",
                                           verbose_name=_('legal rights'))

    # Archiving data
    acquisition_mode      = WeakForeignKey('AcquisitionMode', related_name="collections",
                                            verbose_name=_('mode of acquisition'))
    cnrs_contributor      = CharField(_('CNRS depositor'))
    metadata_author       = WeakForeignKey('MetadataAuthor', related_name="collections",
                                           verbose_name=_('record author'))
    booklet_description   = TextField(_('related documentation'))
    publishing_status     = WeakForeignKey('PublishingStatus', related_name="collections",
                                           verbose_name=_('secondary edition'))
    alt_ids               = CharField(_('copies'))
    comment               = TextField(_('comment'))
    metadata_writer       = WeakForeignKey('MetadataWriter', related_name="collections",
                                           verbose_name=_('record writer'))
    travail               = CharField(_('archiver notes'))
    items_done            = CharField(_('items finished'))
    collector_is_creator  = BooleanField(_('recordist identical to depositor'))
    is_published          = BooleanField(_('published'))
    conservation_site     = CharField(_('conservation site'))

    # Technical data
    code                  = CharField(_('code'), unique=True, required=True,
                                      validators=[is_valid_collection_code])
    old_code              = CharField(_('old code'), unique=False, null=True, blank=True)
    approx_duration       = DurationField(_('approximative duration'))
    physical_items_num    = IntegerField(_('number of components (medium / piece)'))
    physical_format       = WeakForeignKey('PhysicalFormat', related_name="collections",
                                           verbose_name=_('archive format'))
    ad_conversion         = WeakForeignKey('AdConversion', related_name='collections',
                                           verbose_name=_('digitization'))
    state                 = TextField(_('status'))
    a_informer_07_03      = CharField(_('a_informer_07_03'))

    # All
    objects               = MediaCollectionManager()

    def __unicode__(self):
        return self.code

    @property
    def public_id(self):
        return self.code

    @property
    def has_mediafile(self):
        "Tell wether this collection has any media files attached to its items"
        items = self.items.all()
        for item in items:
            if item.file:
                return True
        return False

    def __name_cmp(self, obj1, obj2):
        return unaccent_icmp(obj1.name, obj2.name)

    def countries(self):
        "Return the countries of the items"
        countries = []
        for item in self.items.filter(location__isnull=False):
            for country in item.location.countries():
                if not country in countries:
                    countries.append(country)

        countries.sort(self.__name_cmp)

        return countries
    countries.verbose_name = _("states / nations")

    def ethnic_groups(self):
        "Return the ethnic groups of the items"
        groups = []
        items = self.items.all()
        for item in items:
            if item.ethnic_group and not item.ethnic_group in groups:
                groups.append(item.ethnic_group)

        cmp = lambda a, b: unaccent_icmp(a.value, b.value)
        groups.sort(cmp)

        return groups
    ethnic_groups.verbose_name = _('populations / social groups')

    def computed_duration(self):
        duration = Duration()
        for item in self.items.all():
            duration += item.computed_duration()
        return duration

    computed_duration.verbose_name = _('computed duration')

    @models.permalink
    def get_absolute_url(self):
        return ("telemeta-collection-detail", [self.public_id,])

    def save(self, force_insert=False, force_update=False, user=None, code=None):
        super(MediaCollection, self).save(force_insert, force_update)

    class Meta(MetaCore):
        db_table = 'media_collections'
        ordering = ['code']
        verbose_name = _('collection')


class MediaCollectionRelated(MediaRelated):
    "Collection related media"

    collection      = ForeignKey('MediaCollection', related_name="related", verbose_name=_('collection'))

    class Meta(MetaCore):
        db_table = 'media_collection_related'
        verbose_name = _('collection related media')
        verbose_name_plural = _('collection related media')


class MediaItem(MediaResource):
    "Describe an item"

    element_type = 'item'

    # Main Informations
    title                 = CharField(_('title'))
    alt_title             = CharField(_('original title / translation'))
    collection            = ForeignKey('MediaCollection', related_name="items",
                                       verbose_name=_('collection'))
    recorded_from_date    = DateField(_('recording date (from)'))
    recorded_to_date      = DateField(_('recording date (until)'))

    scientist             = CharField(_('scientist'))
    topic                 = WeakForeignKey('Topic', verbose_name=_('topic'))
    summary               = TextField(_('summary'))
    comment               = TextField(_('remarks'))

    # Geographic and cultural informations
    location              = WeakForeignKey('Location', verbose_name=_('location'))
    location_comment      = CharField(_('location details'))
    cultural_area         = CharField(_('cultural area'))
    ethnic_group          = WeakForeignKey('EthnicGroup', related_name="items",
                                           verbose_name=_('population / social group'))
    language              = CharField(_('language'))
    language_iso          = ForeignKey('Language', related_name="items",
                                       verbose_name=_('ISO language'), blank=True,
                                        null=True, on_delete=models.SET_NULL)
    context_comment       = TextField(_('comments / ethnographic context'))
    moda_execut           = CharField(_('moda_execut'))

    # Musical informations
    vernacular_style      = WeakForeignKey('VernacularStyle', related_name="items",
                                           verbose_name=_('vernacular style'))
    generic_style         = WeakForeignKey('GenericStyle', related_name="items",
                                           verbose_name=_('generic style'))
    author                = CharField(_('author / compositor'))
    contributor           = CharField(_('contributor'))

    # Legal mentions
    organization          = WeakForeignKey('Organization', verbose_name=_('organization'))
    public_access         = CharField(_('access status'), choices=ITEM_PUBLIC_ACCESS_CHOICES,
                                      max_length=16, default="metadata")
    depositor             = CharField(_('depositor'))
    rights                = WeakForeignKey('Rights', verbose_name=_('rights'))
    auto_period_access    = BooleanField(_('automatic access after a rolling period'), default=True)

    # Archiving data
    code                  = CharField(_('code'), unique=True, blank=True)
    old_code              = CharField(_('original code'), unique=False, blank=True)
    track                 = CharField(_('item number'))
    recordist             = CharField(_('recordist'))
    digitalist            = CharField(_('digitalist'))
    collector             = CharField(_('collector'))
    collector_selection   = CharField(_('collector selection'))
    collector_from_collection = BooleanField(_('collector as in collection'))
    digitization_date        = DateField(_('digitization date'))
    publishing_date       = DateField(_('publishing date'))
    creator_reference     = CharField(_('creator reference'))
    external_references   = TextField(_('published references'))
    copied_from_item      = WeakForeignKey('self', related_name="copies",
                                           verbose_name=_('copy of'))
    mimetype              = CharField(_('mime type'), max_length=255, blank=True)

    # Media
    file                  = FileField(_('file'), upload_to='items/%Y/%m/%d',
                                      db_column="filename", max_length=1024)
    url                   = URLField(_('URL'), max_length=512, blank=True)

    # Technical data
    approx_duration       = DurationField(_('approximative duration'))

    # Manager
    objects               = MediaItemManager()

    def keywords(self):
        return ContextKeyword.objects.filter(item_relations__item = self)
    keywords.verbose_name = _('keywords')

    @property
    def public_id(self):
        if self.code:
            return self.code
        return str(self.id)

    @property
    def mime_type(self):
        if not self.mimetype:
            if self.file:
                if os.path.exists(self.file.path):
                    self.mimetype = mimetypes.guess_type(self.file.path)[0]
                    self.save()
                    return self.mimetype
                else:
                    return 'none'
            else:
                return 'none'
        else:
            return _('none')

    class Meta(MetaCore):
        db_table = 'media_items'
        permissions = (("can_play_all_items", "Can play all media items"),
                       ("can_download_all_items", "Can download all media items"), )
        verbose_name = _('item')

    def is_valid_code(self, code):
        "Check if the item code is well formed"
        if not re.match('^' + self.collection.code, self.code):
            return False
        if self.collection.is_published:
            regex = '^' + item_published_code_regex + '$'
        else:
            regex = '^' + item_unpublished_code_regex + '$'
        if re.match(regex, code):
            return True
        return False

    def clean(self):
        if self.code and not self.is_valid_code(self.code):
            raise ValidationError("%s is not a valid item code for collection %s"
                                        % (self.code, self.collection.code))

    def save(self, force_insert=False, force_update=False):
        super(MediaItem, self).save(force_insert, force_update)

    def computed_duration(self):
        "Tell the length in seconds of this item media data"
        return self.approx_duration

    computed_duration.verbose_name = _('computed duration')

    def __unicode__(self):
        if self.title and not re.match('^ *N *$', self.title):
            title = self.title
        else:
            title = unicode(self.collection)
        if self.track:
            title += ' ' + self.track
        return title

    def get_source(self):
        source = None
        if self.file and os.path.exists(self.file.path):
            source = self.file.path
        elif self.url:
            source = self.url
        return source

    @property
    def instruments(self):
        "Return the instruments of the item"
        instruments = []
        performances = MediaItemPerformance.objects.filter(media_item=self)
        for performance in performances:
            instrument = performance.instrument
            alias = performance.alias
            if not instrument in instruments:
                instruments.append(instrument)
            if not alias in instruments:
                instruments.append(alias)

        instruments.sort(self.__name_cmp)
        return instruments

        instruments.verbose_name = _("instruments")

    @models.permalink
    def get_absolute_url(self):
        return ("telemeta-item-detail", [self.public_id,])


class MediaItemRelated(MediaRelated):
    "Item related media"

    item            = ForeignKey('MediaItem', related_name="related", verbose_name=_('item'))

    def save(self, force_insert=False, force_update=False, using=False):
        super(MediaItemRelated, self).save(force_insert, force_update)

    def parse_markers(self, **kwargs):
        # Parse KDEnLive session
        if self.file:
            if self.is_kdenlive_session():
                session = KDEnLiveSession(self.file.path)
                markers = session.markers(**kwargs)
                for marker in markers:
                    m = MediaItemMarker(item=self.item)
                    m.public_id = get_random_hash()
                    m.time = float(marker['time'])
                    m.title = marker['comment']
                    m.save()
                return markers

    class Meta(MetaCore):
        db_table = 'media_item_related'
        verbose_name = _('item related media')
        verbose_name_plural = _('item related media')


class MediaItemKeyword(ModelCore):
    "Item keyword"
    item    = ForeignKey('MediaItem', verbose_name=_('item'), related_name="keyword_relations")
    keyword = ForeignKey('ContextKeyword', verbose_name=_('keyword'), related_name="item_relations")

    class Meta(MetaCore):
        db_table = 'media_item_keywords'
        unique_together = (('item', 'keyword'),)


class MediaItemPerformance(ModelCore):
    "Item performance"
    media_item      = ForeignKey('MediaItem', related_name="performances",
                                 verbose_name=_('item'))
    instrument      = WeakForeignKey('Instrument', related_name="performances",
                                     verbose_name=_('composition'))
    alias           = WeakForeignKey('InstrumentAlias', related_name="performances",
                                     verbose_name=_('vernacular name'))
    instruments_num = CharField(_('number'))
    musicians       = CharField(_('interprets'))

    class Meta(MetaCore):
        db_table = 'media_item_performances'


class MediaItemAnalysis(ModelCore):
    "Item analysis result computed by TimeSide"

    element_type = 'analysis'
    item  = ForeignKey('MediaItem', related_name="analysis", verbose_name=_('item'))
    analyzer_id = CharField(_('id'), required=True)
    name = CharField(_('name'))
    value = CharField(_('value'))
    unit = CharField(_('unit'))

    class Meta(MetaCore):
        db_table = 'media_analysis'
        ordering = ['name']

    def to_dict(self):
        if self.analyzer_id == 'duration':
            if '.' in self.value:
                value = self.value.split('.')
                self.value = '.'.join([value[0], value[1][:2]])
        return {'id': self.analyzer_id, 'name': self.name, 'value': self.value, 'unit': self.unit}


class MediaPart(MediaResource):
    "Describe an item part"
    element_type = 'part'
    item  = ForeignKey('MediaItem', related_name="parts", verbose_name=_('item'))
    title = CharField(_('title'), required=True)
    start = FloatField(_('start'), required=True)
    end   = FloatField(_('end'), required=True)

    class Meta(MetaCore):
        db_table = 'media_parts'
        verbose_name = _('item part')

    def __unicode__(self):
        return self.title

class Playlist(ModelCore):
    "Item, collection or marker playlist"
    element_type = 'playlist'
    public_id      = CharField(_('public_id'), required=True)
    author         = ForeignKey(User, related_name="playlists", db_column="author")
    title          = CharField(_('title'), required=True)
    description    = TextField(_('description'))

    class Meta(MetaCore):
        db_table = 'playlists'

    def __unicode__(self):
        return self.title


class PlaylistResource(ModelCore):
    "Playlist components"
    RESOURCE_TYPE_CHOICES = (('item', 'item'), ('collection', 'collection'),
                             ('marker', 'marker'), ('fonds', 'fonds'), ('corpus', 'corpus'))
    element_type = 'playlist_resource'
    public_id          = CharField(_('public_id'), required=True)
    playlist           = ForeignKey('Playlist', related_name="resources", verbose_name=_('playlist'))
    resource_type      = CharField(_('resource_type'), choices=RESOURCE_TYPE_CHOICES, required=True)
    resource_id        = CharField(_('resource_id'), required=True)

    class Meta(MetaCore):
        db_table = 'playlist_resources'


class MediaItemMarker(MediaResource):
    "2D marker object : text value vs. time (in seconds)"

    element_type = 'marker'

    item            = ForeignKey('MediaItem', related_name="markers", verbose_name=_('item'))
    public_id       = CharField(_('public_id'), required=True)
    time            = FloatField(_('time (s)'))
    title           = CharField(_('title'))
    date            = DateTimeField(_('date'), auto_now=True)
    description     = TextField(_('description'))
    author          = ForeignKey(User, related_name="markers", verbose_name=_('author'),
                                 blank=True, null=True)

    class Meta(MetaCore):
        db_table = 'media_markers'
        ordering = ['time']

    def __unicode__(self):
        if self.title:
            return self.title
        else:
            return self.public_id


class MediaItemTranscoded(MediaResource):
    "Item file transcoded"

    element_type = 'transcoded item'

    item            = models.ForeignKey('MediaItem', related_name="transcoded", verbose_name=_('item'))
    mimetype        = models.CharField(_('mime_type'), max_length=255, blank=True)
    date_added      = DateTimeField(_('date'), auto_now_add=True)
    status          = models.IntegerField(_('status'), choices=ITEM_TRANSODING_STATUS, default=1)
    file            = models.FileField(_('file'), upload_to='items/%Y/%m/%d', max_length=1024, blank=True)

    @property
    def mime_type(self):
        if not self.mimetype:
            if self.file:
                if os.path.exists(self.file.path):
                    self.mimetype = mimetypes.guess_type(self.file.path)[0]
                    self.save()
                    return self.mimetype
                else:
                    return 'none'
            else:
                return 'none'
        else:
            return self.mimetype

    def __unicode__(self):
        if self.item.title:
            return self.item.title + ' - ' + self.mime_type
        else:
            return self.item.public_id + ' - ' + self.mime_type

    class Meta(MetaCore):
        db_table = app_name + '_media_transcoded'


class MediaItemTranscodingFlag(ModelCore):
    "Item flag to know if the MediaItem has been transcoded to a given format"

    item            = ForeignKey('MediaItem', related_name="transcoding", verbose_name=_('item'))
    mime_type       = CharField(_('mime_type'), required=True)
    date            = DateTimeField(_('date'), auto_now=True)
    value           = BooleanField(_('transcoded'))

    class Meta(MetaCore):
        db_table = 'media_transcoding'


class DublinCoreToFormatMetadata(object):
    """ a mapping class to get item DublinCore metadata dictionaries
    in various audio metadata format (MP3, OGG, etc...)"""

    #FIXME: should be given by timeside
    unavailable_extensions = ['wav', 'aiff', 'aif', 'flac', 'webm']

    metadata_mapping = {
                    'mp3' : {
                         'title': 'TIT2', #title2
                         'creator': 'TCOM', #composer
                         'creator': 'TPE1', #lead
                         'identifier': 'UFID', #unique ID
                         'relation': 'TALB', #album
                         'type': 'TCON', #genre
                         'publisher': 'TPUB', #publisher
                         'date': 'TDRC', #year
#                         'coverage': 'COMM',  #comment
                         },
                    'ogg': {
                        'creator': 'artist',
                        'relation': 'album',
                        'all': 'all',
                       },
                    'flac': {
                        'creator': 'artist',
                        'relation': 'album',
                        'all': 'all',
                       },
                    'wav': {
                        'creator': 'artist',
                        'relation': 'album',
                        'all': 'all',
                       },
                    'webm': {
                        'creator': 'artist',
                        'relation': 'album',
                        'all': 'all',
                       },
                    }

    def __init__(self, format):
        self.format = format

    def get_metadata(self, dc_metadata):
        mapp = self.metadata_mapping[self.format]
        metadata = {}
        keys_done = []
        for data in dc_metadata:
            key = data[0]
            value = data[1].encode('utf-8')
            if value:
                if key == 'date':
                    value = value.split(';')[0].split('=')
                    if len(value) > 1:
                        value  = value[1]
                        value = value.split('-')[0]
                    else:
                        value = value[0].split('-')[0]
                if key in mapp:
                    metadata[mapp[key]] = value.decode('utf-8')
                elif 'all' in mapp.keys():
                    metadata[key] = value.decode('utf-8')
                keys_done.append(key)
        return metadata


class MediaCorpus(MediaBaseResource):
    "Describe a corpus"

    element_type = 'corpus'
    children_type = 'collections'

    children = models.ManyToManyField(MediaCollection, related_name="corpus",
                                      verbose_name=_('collections'),  blank=True, null=True)
    recorded_from_year    = IntegerField(_('recording year (from)'))
    recorded_to_year      = IntegerField(_('recording year (until)'))

    objects = MediaCorpusManager()

    @property
    def public_id(self):
        return self.code
    
    @property
    def has_mediafile(self):
        for child in self.children.all():
            if child.has_mediafile:
                return True
        return False

    class Meta(MetaCore):
        db_table = 'media_corpus'
        verbose_name = _('corpus')
        verbose_name_plural = _('corpus')

    @models.permalink
    def get_absolute_url(self):
        return ("telemeta-corpus-detail", [self.public_id,])


class MediaFonds(MediaBaseResource):
    "Describe fonds"

    element_type = 'fonds'
    children_type = 'corpus'

    children = models.ManyToManyField(MediaCorpus, related_name="fonds",
                                      verbose_name=_('corpus'), blank=True, null=True)

    objects = MediaFondsManager()

    @property
    def public_id(self):
        return self.code

    @property
    def has_mediafile(self):
        for child in self.children.all():
            if child.has_mediafile:
                return True
        return False

    @models.permalink
    def get_absolute_url(self):
        return ("telemeta-fonds-detail", [self.public_id,])

    class Meta(MetaCore):
        db_table = 'media_fonds'
        verbose_name = _('fonds')
        verbose_name_plural = _('fonds')


class MediaCorpusRelated(MediaRelated):
    "Corpus related media"

    resource = ForeignKey(MediaCorpus, related_name="related", verbose_name=_('corpus'))

    class Meta(MetaCore):
        db_table = 'media_corpus_related'
        verbose_name = _('corpus related media')
        verbose_name_plural = _('corpus related media')


class MediaFondsRelated(MediaRelated):
    "Fonds related media"

    resource = ForeignKey(MediaFonds, related_name="related", verbose_name=_('fonds'))

    class Meta(MetaCore):
        db_table = 'media_fonds_related'
        verbose_name = _('fonds related media')
        verbose_name_plural = _('fonds related media')

