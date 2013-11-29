function ResourceMap(list, cfg) {
    var  that      = this;
    that.list      = null;
    that.container = null;
    that.map       = null;

    that.init = function(list, cfg) {
        that.cfg = cfg;
        $(document).ready(function() {
            that.log("init");
            that.list = $(list);
            that.container = $('<div/>').addClass('gmap').css({'width': '100%', 'height': 300});
            that.list.css('display', 'none').after(that.container);
            var resizeTimer = null;
            $(window).resize(function() {
                if (resizeTimer)
                    clearTimeout(resizeTimer);
                resizeTimer = setTimeout(that.resize, 100);
            });
            that.resize();
        });
        
        
            that.createMap();
            that.parseResources();
            // $(window).bind('unload', google.maps.Unload);
        

    }

    that.resize = function() {
        if (that.container.css('display') == 'block') {
            newHeight = that.container.height() + $(window).height() - $("#layout").height() + $('#footer').height();
            if (newHeight < 300)
                newHeight = 300;
            if (newHeight != that.container.height()) {
                that.container.height(newHeight);
                if (that.map) {
                    that.map.checkResize();
                }
            }

        }
    }

    that.toggle = function(force) {
        force = typeof(force) == "undefined" ? null : force;
        if (force == 'list' || (!force && that.list.css('display') == 'none')) {
            that.container.css('display', 'none');
            that.list.css('display', 'block');
        } else {
            that.container.css('display', 'block');
            that.list.css('display', 'none');
            that.resize();
        }
    }

    that.log = function(msg) {
        if (typeof(console) != "undefined" && typeof(console.log) != undefined) {
            console.log(msg);
        }
    }

    that.makeInfoBox = function(name, link, linktitle) {
        var info = $('<div/>').addClass('resourcemap-info');
        info.append($('<h2/>').text(name));
        info.append($('<a/>').attr('href', link).text(linktitle));
        return info.wrap('<div/>').parent().html();
    }

    that.showResourceInfo = function(marker, resourceElement) {
        var info = $('<div/>').addClass('resourcemap-info');
        marker.openInfoWindowHtml(info.get(0));
        var re  = /^resource-/;
        var id  = resourceElement.attr('id').replace(re, '');
        var uri = that.cfg.countryInfoUri.replace('RESOURCEID', id);
        
        $.get(uri, function(data) {
            info.html(data);
            //marker.openInfoWindowHtml(info.get(0));
        });
    }

    that.parseResources = function() {
        $('.resourcemap-element').each(function(i, e) {
            e = $(e)
            var input     = e.find('.resourcemap-lat');
            if (input.length) {
                var lat       = parseFloat(input.attr('value'));
                var lng       = parseFloat(e.find('.resourcemap-lng').attr('value'));
                //var name      = $.trim(e.find('.resourcemap-name').text());
                //var link      = e.find('a').attr('href');
                //var linktitle = e.find('a').attr('title');
                var marker    = new google.maps.Marker(new google.maps.LatLng(lat, lng), {title: name, map: that.map});
                //var info      = that.makeInfoBox(name, link, linktitle);
                google.maps.event.addListener(marker, "click", function() {
                    that.showResourceInfo(marker, e);
                    //marker.openInfoWindowHtml(info);
                });
                
            }
        });
    }        

    that.createMap = function() {
          var mapOptions = {
            zoom: 2,
            center: new google.maps.LatLng(42.0, 6.0)
            };
        that.log("GMap loaded");    
        that.map = new google.maps.Map(that.container[0], mapOptions);
        // var bounds = new google.maps.LatLngBounds();
        // that.map.setCenter(new google.maps.LatLng(0, 0), that.map.getBoundsZoomLevel(bounds)); // France
        // that.map.setUIToDefault();
    }

    that.init(list, cfg);
}


function initialize() {
    var resourceMap = new ResourceMap('.continents', {
    'countryInfoUri': '/geo/country_info/RESOURCEID/'});
}


function loadScript() {
  var script = document.createElement('script');
  script.type = 'text/javascript';
  script.src = 'https://maps.googleapis.com/maps/api/js?v=3.exp&sensor=false&callback=initialize';
  document.body.appendChild(script);
}
