1.5
+++++

 * Compatible with Django 1.6.x
 * Huge refactor of all forms, detail and edit views
 * Main styles are now based Bootstrap 3.x
 * Update models thanks to the CREM needs
 * Compatible with TimeSide 0.6.x

1.4.6
+++++

 * Drastically improve collection zip packaqe streaming thanks to zipstream (check NEW dependencies)
 * Compatible with TimeSide >= 0.5.2
 * Add URL field to item so that a external sound can be indexed and streamed
 * Add TIMESIDE_AUTO_ZOOM in settings to auto toggle the player in zooming mode
 * Add TIMESIDE_DEFAULT_GRAPHER_ID in settings to select the default grapher in the player
 * Add minor migrations
 * Fix marker display bug

1.4.5
+++++

 * Collection and Item regex in settings allowed
 * Change resource list filtering rules
 * Add KdenLive session parsers and auto faders to auto tag audio or video timeline
 * Add ffmpeg based transcoding tools
 * Add enumerations replacing methods
 * Add chat rooms for enumerations
 * Cleanup some useless model properties
 * Many, many and many bugfixes
 * Last version compatible with TimeSide 0.4.x
 * Please check the new dependencies in setup.py
 * As always after upgrading: ./manage.py migrate telemeta

1.4.4
+++++

 * no new fancy functions
 * full using of static files which are now in static/ (htdocs/ is now deprecated)
 * IMPORTANT : upgrade TimeSide to 0.4.1, add 'timeside' to INSTALLED_APPS and do: ./manage.py collectstatic
 * add various buttons, various bugfixes
 * after upgrading, always do: ./manage.py migrate

telemeta (1.4.3-1) unstable; urgency=low

 * add solr-thumbnail for automatic thumbnail handling of all related media images (please install)
 * add static media handling for solr and all various telemeta public files
 * fix some wrong user properties
 * SECURITY: you need to move your TELEMETA_EXPORT_CACHE_DIR from TELEMETA_CACHE_DIR cache (see example/sandbox_sqlite/settings.py)
 * EXPERIMENTAL: WebM and MP4 video handling for items, NO transcode but decode, add a nice video.js player
 * RECOMMEND: install django-extensions
 * transitional package to 1.5 (maybe 1.4.4 *soon*)

telemeta (1.4.2-1) unstable; urgency=low

 * add user revisions to user profile
 * move all edit buttons to main edit pages
 * new Format object and various enumerations
 * add last revision to item detail
 * various bugfixes

telemeta (1.4.1-1) unstable; urgency=low

 * Fix a bug for related media title parsing

telemeta (1.4-1) unstable; urgency=low

For users:

 * add a Desk providing links to home and personal data
 * add Fonds, Corpus and their related media to the models and to the search engine
 * add some fancy drop down menus for main tabs
 * add video media handling (WebM formats only and with the last TimeSide master branch)
 * add playlist metadata editor
 * fix some sad bugs for YouTube related URLs and previews
 * cleanup admin page
 * add auto saving now for all searches !
 * add "My Searches" modules to user lists with search direct link
 * add RSS feeds for last changes of all users
 * better icon views
 * many bugfixes !

For developers and maintainers:

 * a new setting parameter: TELEMETA_DOWNLOAD_FORMATS = ('wav', 'mp3', 'webm') or whatever
 * before upgrading, you need to BACKUP and manually delete old wrong MediaCorpus and MediaCorpusRelated tables
 * we now use South for data model migration (./manage.py migrate telemeta). Add it to your apps. See INSTALL.rst. Email me if any pb!

-- Guillaume Pellerin <yomguy@parisson.com>  Fri, 10 Feb 2012 16:10:22 +0200

telemeta (1.3-1) unstable; urgency=low

 * add related media objects to collections and items (mime type detection, image preview, URL only capable, YouTube URL detection and preview)
 * add "Sound" filters to collection lists and search results
 * add a scrollbar to marker lists
 * add dependencies to setup.py
 * various bugfixes
 * developers now use Git

-- Guillaume Pellerin <yomguy@parisson.com>  Mon, 01 Dec 2011 17:10:22 +0200

telemeta (1.2-1) unstable; urgency=low

 * fix the whole setup

-- Guillaume Pellerin <yomguy@parisson.com>  Mon, 31 Oct 2011 13:46:22 +0200

telemeta (1.1-1) unstable; urgency=low

 * fix OAI repository names, coverages and headers in according with TGE Adonis specs
 * replace home (index) playlist by 3 random nice embedded players (public items only)
 * add "Sound" filter to the item list for easier access to sound items
 * fix various bugs

-- Guillaume Pellerin <yomguy@parisson.com>  Fri, 28 Oct 2011 11:33:22 +0200

telemeta (1.0-1) unstable; urgency=low

 * Embedable resizable audio player with an iframe HTML object
 * Text popup windows following time markers during playing
 * 2 new user permissions to allow full download and audio play
 * Delete buttons on each collection and item page
 * Audio analyses are now recorded in the database
 * Transcoding of the whole files is now checked
 * New "Users" tab
 * Better and faster TimeSide player loading
 * Sorting of all enumerations and lists
 * Full english > french translation
 * Reorganize django views (faster page loading)
 * More revisions and details in the main RSS feed
 * Bugfixes
 * Fix some field titles for the CREM
 * Fix public access rights
 * Many CSS fixes
 * Fix multiple playings when hiting play more than one time

-- Guillaume Pellerin <yomguy@parisson.com>  Fri, 27 Jun 2011 11:33:22 +0200

telemeta (0.9.4-1) unstable; urgency=low

 * New visual theme
 * Playing all kinds of audio files thanks to  TimeSide (even video files !)
 * Editing items, collections and all lists
 * Managing temporal markers to get time description of the archives
 * Userspace playlist management
 * Admin User management and profiling
 * Password retrieval and management
 * CSV export of user playlists
 * RSS feeds for last changes
 * Full french and english localization (interface, forms)
 * Optimization of audio analysis
 * MANY bugfixes

-- Guillaume Pellerin <yomguy@parisson.com>  Fri, 01 Jun 2011 11:33:22 +0200

 telemeta (0.8-1) unstable; urgency=low

  * New upstream release
  * See http://telemeta.org/log/ for the entire changelog

 -- Guillaume Pellerin <yomguy@parisson.com>  Fri, 06 May 2011 11:33:22 +0200

telemeta (0.4-1) unstable; urgency=low

  * New upstream release
  * See http://telemeta.org/log/ for the entire changelog

 -- Guillaume Pellerin <yomguy@altern.org>  Tue, 17 Mar 2009 01:46:51 +0100

telemeta (0.3.3-1) unstable; urgency=low

  * Add django 1.0 compatibility (no backward compatibility in most cases)
  * Modify dependencies and manuals

 -- Guillaume Pellerin <yomguy@altern.org>  Tue, 30 Sep 2008 02:45:36 +0200

telemeta (0.3.2-4) unstable; urgency=low

  * Change license from BSD to CeCILL

 -- Guillaume Pellerin <yomguy@altern.org>  Fri, 19 Sep 2008 15:38:48 +0200

telemeta (0.3.2-3) unstable; urgency=low

  * Fix max_digits

 -- Guillaume Pellerin <yomguy@altern.org>  Mon, 15 Sep 2008 13:46:11 +0200

telemeta (0.3.2-2) unstable; urgency=low

  * Add analyzers

 -- Guillaume Pellerin <yomguy@altern.org>  Mon, 15 Sep 2008 11:40:06 +0200

telemeta (0.3.2-1) unstable; urgency=low

  * Add analysis plugin component and views
  * Add wav2png.py objects and views
  * Add audiolab python library
  * Modify dependencies

 -- Guillaume Pellerin <yomguy@altern.org>  Thu, 28 Aug 2008 01:13:14 +0200

telemeta (0.3.1-1beta) unstable; urgency=low

  * Clear some install features
  * Change waveform color
  * Change menu order
  * Change link order at home
  * Fix spectrogram
  * Fix tuple bug for version
  * Modify setup method (distutils)
  * 2nd layout v0.4 item/view + item/edit
  * Item instruments prototype display
  * Hide empty fields on collection and item detail display
  * Layout breaks under 1024x768 : fixbug
  * image search, css pagination
  * search results: display collection tab by default if there's no item
  * fix search combining country/continent and ethnic group
  * layout v0.4 item/view + item/edit
  * advanced search form/results + fix wrong revert
  * advanced seach css formulaire
  * fix urls
  * affichage mediafile, overflow pour spectrogram
  * hide 4D internal field compil_face_plage
  * do not print duplicate countries and ethnic groups on collection detail
  * item/collection dublincore + fixbug css
  * write item and not items with a single result
  * enable searching items by publish date and collections by ethnic group
  * fix advanced search by title; fix empty search
  * affichage item v1 + bug largeur liste definition list
  * (re) fix build_query_string filter
  * collection dublin core
  * collections avec tous les champs
  * fix build_query_string filter
  * item quick search now also searches the creator (auteur) field
  * improved search; search results are now paginated, displaying either
  * items or collections, with a tab view
  * affichage collections + modifs css
  * sort related items by id on collection detail
  * advanced search: add missing templates
  * model modularization ; add is_published() method for collections
  * model modularization
  * add advanced search
  * models: code cleanup and new docstrings
  * Rewrite README and INSTALL
  * Show a table for 'normal' data view
  * Logo Telemeta FINAL v2

 -- Guillaume Pellerin <yomguy@altern.org>  Thu, 28 Aug 2008 01:11:19 +0200

telemeta (0.3.0-1) unstable; urgency=low

  * Changed README and INSTALL
  * fix spectrograms names
  * accept underscore in viz id
  * setting version to 'SVN' on trunk
  * fix items and collections fields display ordering + make item title
  * optional for django admin
  * use css overflow instead of iframe for visualization scrolling
  * Added metadata to OGG stream
  * Tuned max sample lengths to reasonable values
  * Tuned max sample lengths to reasonable values
  * Changed time_limit to 300 (5mn) for Octave
  * Added main tags to streamed mp3. Closes: #9
  * Made Octave quiet
  * Downsampling data for waveform2
  * Add an iframe to scroll on visualizers
  * Cleaned OctaveCoreVisualizer to avoid wrong subprocess calls
  * Fix the maximum displayed length to 10s max for Octave visualizers
  * Added octave2.9 dependency
  * Added Waveform2 and Spectrogram2 visualization components
  * Clean up
  * Removed old/
  * fix #28: use item id from export filename. WARNING: require crem data r3
  * make htdocs variable dynamic and add draft for 0.3 INSTALL
  * Fixed ExportProcessError
  * Remove sox piping for FLAC
  * simplify !TelemetaError
  * Create ExportProcessError class in export.api
  * cast double literals (breaks on Debian Sarge)
  * remove extra space in M3U playlist (failed with Amarok)
  * Fixed #26 partially for downloading but not for flash playing
  * remove unused logger instance and duplicated telemeta version
  * variable, use telemeta url variable + new telemeta_url template tag
  * soften footer logo
  * decrease homepage links size
  * tracify menu bar, add footer, homepage links and fix items list in
  * collection detail
  * add version in __init__.py and telemeta_version template tag
  * optimize and rename BackupBuilder to CollectionSerializer
  * add method to retrieve items that do not belong to any collection
  * display id on item detail
  * rename !FloatField to !DecimalField for django svn !r5302
  * Cleaned mp3 exporter
  * Fixed syntax problem
  * Restore Jeroen Wijering's Flash MP3 Player
  * add backup core and command line tool
  * consolidate MediaCore.to_dom() and fix encoding
  * Adds main id3 tags during MP3 streaming
  * Moved audio generator to ExporterCore.core_process
  * add variable for static files root
  * use named urls for static files
  * add to_dom() to models
  * renaming views to web
  * renaming web.py to base.py
  * add geographic navigator, coverage dc mapping to collection + other fixes
  * added collection playlists in m3u and xspf formats
  * embedded flash mp3 player in both collection and item displays.
  * Remark: there are two players available, you can switch them in the templates
  * media objects IDs are now validated at model level
  * experimenting new logo by Julia
  * trying some new layout + cleaned css
  * renamed &#34;dictionaries&#34; to &#34;enumerations&#34;
  * new PublishingStatus enumerations model (you simply need to syncdb)
  * Telemeta logos v1
  * convert DC elements values to strings
  * fix doblock and spacing
  * add default empty elements attribute for code clarity
  * fix css issue between visualization and submenu
  * add dublin core modelization and new to_dublincore() model methods
  * improved dublin core mapping
  * add dublin core HTML-based views of collections and items
  * fixed URL handling with non aplhanumeric record IDs
  * fix #21: the web view now properly handle export streams
  * turn the model list() method into the tolist template filter
  * new submenu template block + css fixes
  * Tried new stream function in web.py, but....
  * Partially fixes #19 by changing MediaCollection.copied_from properties.
  * Made all exporters generators. Closes: #8 . Input audio raw data is
  * now passed into sox while encoding (no decoding needed anymore...)
  * Clean some stings
  * Made Mp3Exporter a generator. The exported file is still written in the cache.
  * misc template fixes
  * fix items urls
  * add LEM item fields + other fixes
  * add paging and simplify layout
  * bundle snack python bindings
  * svn:ignore .pyc and .swp files
  * add templatetags
  * use named urls, add paging to collection, and others
  * add LEM collection fields
  * change visualization layout and waveform color
  * add visualization to web item detail view
  * add visualization components (waveform, spectrogram)
  * ticket #10: mark IExporter.process() options argument as optional
  * Replaced all tabs by spaces in export. Closes: #18
  * typo
  * added license headers + cleanup
  * Temporary fixed mp3 date in urls.py
  * created htdocs dir, images subdir and moved the css dir
  * renamed the core css stylesheet
  * updated css, new stylesheet for the admin
  * Fixed indent pb
  * Fixed ogg verbose
  * Made options optional. Closes: #10
  * Added Mp3Exporter with (very) partial mapping of DublinCore fields.
  * fixed quick search form css/layout on Firefox
  * No metadata in caching path (just ext/item_id.ext). No verbose by default
  * web interface: added quick search and fixed export download
  * Added Samalyse to COPYING
  * coupled the web interface with the export layer
  * improved collections and items browsing
  * minor CSS improvements
  * now using Django typical models instead of &#34;dynamic&#34; ones
  * made simple models based on Dublin Core elements
  * Fixed Default call and verbose
  * Move default.py to old/
  * Fixed export verbose mode in option dict (see export_test)
  * Added Trac Components links. Added options dict to exporter arguments
  * Add pre and post process in CoreExporter. Main calls to OggExporter

 -- Guillaume Pellerin <yomguy@altern.org>  Wed, 28 May 2007 22:28:42 +0200

telemeta (0.2.5-2) unstable; urgency=low

  * Fixed --help page

 -- Guillaume Pellerin <yomguy@altern.org>  Wed, 10 Jan 2007 12:01:13 +0100

telemeta (0.2.5-1) unstable; urgency=low

  * Fixed --create and --backup option behaviors, thanks to Olivier Guilyardi
  * Created the Collection class and interface
  * Fixed error messages
  * Made the collection XML file saved in collection dir AND user default dir

 -- Guillaume Pellerin <yomguy@altern.org>  Mon,  8 Jan 2007 02:50:04 +0100

telemeta (0.2.4-3) unstable; urgency=low

  * Fixed README and INSTALL pages

 -- Guillaume Pellerin <yomguy@altern.org>  Thu,  4 Jan 2007 18:56:05 +0100

telemeta (0.2.4-2) unstable; urgency=low

  * Fixed --help menu and man page

 -- Guillaume Pellerin <yomguy@altern.org>  Wed,  3 Jan 2007 22:18:05 +0100

telemeta (0.2.4-1) unstable; urgency=low

  * Rewrited the whole main structure
  * Defined a class and xml for consts
  * Fixed --erase-media option
  * Fixed --recover option
  * Added --create option: creates a database repository and default database xml
  * Added --backup option: backups a media to the database
  * Added --album option: proccesses an entire directory (one shot album)
  * Added --from-xml: takes tags and opts in original xml source
  * Added --all-default: chooses default argument for all question
  * Added --par2 : forces par2 file creation
  * Added --rsync : synchronizes database to a remote server (ssh+rsync)
  * Added --clean-strings : cleans input strings

 -- Guillaume Pellerin <pellerin@parisson.com>  Wed, 3 Jan 2007 18:55:52 +0100

telemeta (0.2.3-3) unstable; urgency=low

  * Fixed --force mode bug

 -- Guillaume Pellerin <pellerin@parisson.com>  Wed, 22 Nov 2006 12:33:52 +0100

telemeta (0.2.3-2) unstable; urgency=low

  * fixed non audio file detection with 'file' command

 -- Guillaume Pellerin <pellerin@parisson.com>  Wed, 15 Nov 2006 15:30:10 +0100

telemeta (0.2.3-1) unstable; urgency=low

    * Added python-xml parser dependency :
      xml tag files are now exported to user default directory and in dir_in.
    * Added par2 dependency : creates secure recovery key file with the "par2" method
    * Added python-mutagen dependency : new tagging functions
    * Cleaned : audio functions
    * Fixed : help page
    * Debianized

 -- Guillaume Pellerin <pellerin@parisson.com>  Tue, 01 Nov 2006 00:25:46 +0100

telemeta (0.2.2) unstable; urgency=low

    * Defined : the tag and option lists
    * Created : main audio functions
    * Created : main tags functions

 -- Guillaume Pellerin <pellerin@parisson.com>  Tue, 14 Jul 2006 00:00:01 +0100

telemeta (0.1) unstable; urgency=low

    * Initial release
    * Created : First flac, ogg, mp3 exporting, tagging with basic functions

 -- Guillaume Pellerin <pellerin@parisson.com>  Tue, 01 May 2006 23:45:42 +0200
