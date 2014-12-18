# -*- coding: utf-8 -*-
# Copyright (C) 2007-2010 Samalyse SARL
# Copyright (C) 2010-2012 Parisson SARL

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

# Authors: Olivier Guilyardi <olivier@samalyse.com>
#          Guillaume Pellerin <yomguy@parisson.com>


from telemeta.views.core import *


class HomeView(object):
    """Provide general web UI methods"""

    def home(self, request):
        """Render the index page"""

        template = loader.get_template('telemeta/home.html')

        N = 3   # max number of pub items

        sound_items = MediaItem.objects.sound_public()
        count = sound_items.count()

        if count == 0:
            sound_pub_item = None
            sound_pub_items = None

        elif count == 1:
            sound_pub_item = sound_items[0]
            sound_pub_items = [sound_items[0], sound_items[0]]

        elif count == 2:
            sound_pub_item = sound_items[0]
            sound_pub_items = [sound_items[0], sound_items[1]]

        elif count > 2:
            indexes = random.sample(range(count-1), N)
            sound_pub_item = sound_items[indexes[0]]
            sound_pub_items = [sound_items[indexes[i]] for i in range(1, N)]

        revisions = get_revisions(25)
        context = RequestContext(request, {
                    'page_content': pages.get_page_content(request, 'home', ignore_slash_issue=True),
                    'revisions': revisions,  'sound_pub_items': sound_pub_items,
                    'sound_pub_item': sound_pub_item })
        return HttpResponse(template.render(context))

    def lists(self, request):
        """Render the home page"""

        if request.user.is_authenticated():
            template='telemeta/lists.html'
            playlists = get_playlists(request)
            revisions = get_revisions(100)
            searches = Search.objects.filter(username=request.user)
            user_revisions = get_revisions(25, request.user)
            return render(request, template, {'playlists': playlists, 'searches': searches,
                                              'revisions': revisions, 'user_revisions': user_revisions })
        else:
            template = 'telemeta/messages.html'
            mess = ugettext('Access not allowed')
            title = ugettext('Lists') + ' : ' + mess
            description = ugettext('Please login or contact the website administator to get a private access.')
            messages.error(request, title)
            return render(request, template, {'description' : description})

    def edit_search(self, request, criteria=None):
        year_min, year_max = MediaCollection.objects.all().recording_year_range()
        rec_years = year_min and year_max and range(year_min, year_max + 1) or []
        year_min, year_max = MediaCollection.objects.all().publishing_year_range()
        pub_years = year_min and year_max and range(year_min, year_max + 1) or []
        if request.user.is_authenticated():
            searches = Search.objects.filter(username=request.user)
        else:
            searches = []
        return render(request, 'telemeta/search_criteria.html', {
            'rec_years': rec_years,
            'pub_years': pub_years,
            'ethnic_groups': MediaItem.objects.all().ethnic_groups(),
            'criteria': criteria,
            'searches': searches,
        })

    def handle_oai_request(self, request):
        host = request.META['HTTP_HOST']
        datasource  = TelemetaOAIDataSource()
        repository_name = settings.TELEMETA_ORGANIZATION
        url         = 'http://' + host + request.path
        admin       = settings.ADMINS[0][1]
        provider    = oai.DataProvider(datasource, repository_name, url, admin)
        args        = request.GET.copy()
        args.update(request.POST)
        return HttpResponse(provider.handle(args), mimetype='text/xml')

    def render_flatpage(self, request, path):
        try:
            content = pages.get_page_content(request, path)
        except pages.MalformedPagePath:
            return redirect(request.path + '/')

        if isinstance(content, pages.PageAttachment):
            return HttpResponse(content, content.mimetype())
        else:
            return render(request, 'telemeta/flatpage.html', {'page_content': content })

    def logout(self, request):
        auth.logout(request)
        return redirect('telemeta-home')

    def search(self, request, type = None):
        """Perform a search through collections and items metadata"""
        collections = MediaCollection.objects.enriched()
        items = MediaItem.objects.enriched()
        corpus = MediaCorpus.objects.all()
        fonds  = MediaFonds.objects.all()
        input = request.REQUEST
        criteria = {}

        switch = {
            'pattern': lambda value: (
                collections.quick_search(value),
                items.quick_search(value),
                corpus.quick_search(value),
                fonds.quick_search(value),
                ),
            'title': lambda value: (
                collections.word_search('title', value),
                items.by_title(value),
                corpus.word_search('title', value),
                fonds.word_search('title', value)),
            'location': lambda value: (
                collections.by_location(Location.objects.get(name=value)),
                items.by_location(Location.objects.get(name=value))),
            'continent': lambda value: (
                collections.by_continent(value),
                items.filter(continent = value)),
            'ethnic_group': lambda value: (
                collections.by_ethnic_group(value),
                items.filter(ethnic_group = value),
                EthnicGroup.objects.get(pk=value)),
            'creator': lambda value: (
                collections.word_search('creator', value),
                items.word_search('collection__creator', value)),
            'collector': lambda value: (
                collections.by_fuzzy_collector(value),
                items.by_fuzzy_collector(value)),
            'rec_year_from': lambda value: (
                collections.by_recording_year(int(value), int(input.get('rec_year_to', value))),
                items.by_recording_date(datetime.date(int(value), 1, 1),
                                        datetime.date(int(input.get('rec_year_to', value)), 12, 31))),
            'rec_year_to': lambda value: (collections, items),
            'pub_year_from': lambda value: (
                collections.by_publish_year(int(value), int(input.get('pub_year_to', value))),
                items.by_publish_year(int(value), int(input.get('pub_year_to', value)))),
            'pub_year_to': lambda value: (collections, items),
            'sound': lambda value: (
                collections.sound(),
                items.sound()),
            'instrument': lambda value: (
                collections.by_instrument(value),
                items.by_instrument(value)),
        }

        for key, value in input.items():
            func = switch.get(key)
            if func and value and value != "0":
                try:
                    res = func(value)
                    if len(res)  > 4:
                        collections, items, corpus, fonds, value = res
                    elif len(res) == 4:
                        collections, items, corpus, fonds = res
                    elif len(res) == 3:
                        collections, items, value = res
                        corpus = corpus.none()
                        fonds = fonds.none()
                    else:
                        collections, items = res
                        corpus = corpus.none()
                        fonds = fonds.none()

                except ObjectDoesNotExist:
                    collections = collections.none()
                    items = items.none()
                    corpus = corpus.none()
                    fonds = fonds.none()

                criteria[key] = value

        # Save the search
        user = request.user
        if user:
            if user.is_authenticated():
                search = Search(username=user)
                search.save()
                if criteria:
                    for key in criteria.keys():
                        value = criteria[key]
                        if key == 'ethnic_group':
                            try:
                                group = EthnicGroup.objects.get(value=value)
                                value = group.id
                            except:
                                value = ''
                        criter = Criteria(key=key, value=value)
                        criter.save()
                        search.criteria.add(criter)
                    search.save()

        if type is None:
            if collections.count():
                type = 'collections'
            else:
                type = 'items'

        if type == 'items':
            objects = items
        elif type == 'collections':
            objects = collections
        elif type == 'corpus':
            objects = corpus
        elif type == 'fonds':
            objects = fonds

        return list_detail.object_list(request, objects,
            template_name='telemeta/search_results.html', paginate_by=20,
            extra_context={'criteria': criteria, 'collections_num': collections.count(),
                'items_num': len(items), 'corpus_num': corpus.count(), 'fonds_num': fonds.count(),
                'type' : type,})

    def complete_location(self, request, with_items=True):
        input = request.REQUEST

        token = input['q']
        limit = int(input['limit'])
        if with_items:
            locations = MediaItem.objects.all().locations()
        else:
            locations = Location.objects.all()

        locations = locations.filter(name__istartswith=token).order_by('name')[:limit]
        data = [unicode(l) + " (%d items)" % l.items().count() for l in locations]

        return HttpResponse("\n".join(data))

    @method_decorator(login_required)
    def users(self, request):
        users = User.objects.all().order_by('last_name')
        return render(request, 'telemeta/users.html', {'users': users})


class SearchView(ListView):
    """Perform a search through resources"""

    template_name='telemeta/search_results.html'
    paginate_by = 20

    def get_queryset(self):
        input = self.request.GET
        self.criteria = {}

        self.type = None
        if 'type' in self.kwargs:
            self.type = self.kwargs['type']

        self.collections = MediaCollection.objects.enriched()
        self.items = MediaItem.objects.enriched()
        self.corpus = MediaCorpus.objects.all()
        self.fonds  = MediaFonds.objects.all()

        switch = {
            'pattern': lambda value: (
                self.collections.quick_search(value),
                self.items.quick_search(value),
                self.corpus.quick_search(value),
                self.fonds.quick_search(value),
                ),
            'title': lambda value: (
                self.collections.word_search('title', value),
                self.items.by_title(value),
                self.corpus.word_search('title', value),
                self.fonds.word_search('title', value)),
            'location': lambda value: (
                self.collections.by_location(Location.objects.get(name=value)),
                self.items.by_location(Location.objects.get(name=value))),
            'continent': lambda value: (
                self.collections.by_continent(value),
                self.items.filter(continent = value)),
            'ethnic_group': lambda value: (
                self.collections.by_ethnic_group(value),
                self.items.filter(ethnic_group = value),
                EthnicGroup.objects.get(pk=value)),
            'creator': lambda value: (
                self.collections.word_search('creator', value),
                self.items.word_search('collection__creator', value)),
            'collector': lambda value: (
                self.collections.by_fuzzy_collector(value),
                self.items.by_fuzzy_collector(value)),
            'rec_year_from': lambda value: (
                self.collections.by_recording_year(int(value), int(input.get('rec_year_to', value))),
                self.items.by_recording_date(datetime.date(int(value), 1, 1),
                                        datetime.date(int(input.get('rec_year_to', value)), 12, 31))),
            'rec_year_to': lambda value: (self.collections, self.items),
            'pub_year_from': lambda value: (
                self.collections.by_publish_year(int(value), int(input.get('pub_year_to', value))),
                self.items.by_publish_year(int(value), int(input.get('pub_year_to', value)))),
            'pub_year_to': lambda value: (self.collections, self.items),
            'sound': lambda value: (
                self.collections.sound(),
                self.items.sound()),
            'instrument': lambda value: (
                self.collections.by_instrument(value),
                self.items.by_instrument(value)),
        }

        for key, value in input.items():
            func = switch.get(key)
            if func and value and value != "0":
                try:
                    res = func(value)
                    if len(res)  > 4:
                        self.collections, self.items, self.corpus, self.fonds, value = res
                    elif len(res) == 4:
                        self.collections, self.items, self.corpus, self.fonds = res
                    elif len(res) == 3:
                        self.collections, self.items, value = res
                        self.corpus = self.corpus.none()
                        self.fonds = self.fonds.none()
                    else:
                        self.collections, self.items = res
                        self.corpus = self.corpus.none()
                        self.fonds = self.fonds.none()

                except ObjectDoesNotExist:
                    self.collections = self.collections.none()
                    self.items = self.items.none()
                    self.corpus = self.corpus.none()
                    self.fonds = self.fonds.none()

                self.criteria[key] = value

        # Save the search
        user = self.request.user
        if user:
            if user.is_authenticated():
                search = Search(username=user)
                search.save()
                if self.criteria:
                    for key in self.criteria.keys():
                        value = self.criteria[key]
                        if key == 'ethnic_group':
                            try:
                                group = EthnicGroup.objects.get(value=value)
                                value = group.id
                            except:
                                value = ''
                        criter = Criteria(key=key, value=value)
                        criter.save()
                        search.criteria.add(criter)
                    search.save()

        if self.type is None:
            if self.collections.count():
                self.type = 'collections'
            else:
                self.type = 'items'

        if self.type == 'items':
            objects = self.items
        elif self.type == 'collections':
            objects = self.collections
        elif self.type == 'corpus':
            objects = self.corpus
        elif self.type == 'fonds':
            objects = self.fonds

        return objects

    def get_context_data(self, *args, **kwargs):
        context = super(SearchView, self).get_context_data(*args, **kwargs)
        context['criteria'] = self.criteria
        context['collections_num'] =  self.collections.count()
        context['items_num'] = self.items.count()
        context['corpus_num']  = self.corpus.count()
        context['fonds_num'] = self.fonds.count()
        context['type'] = self.type
        return context
