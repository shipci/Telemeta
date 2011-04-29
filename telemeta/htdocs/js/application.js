
//Class for global functions.
//Note that the dollar sign is a reserved keyword in some browsers
//(see http://davidwalsh.name/dollar-functions)
//which might be in conflict with jQuery dollar sign

//PENDING: use static method?
//adds a move function to the array object.
//moves the element at position from into to position
//returns from if no move was accomplished, ie when either:
//1) from or to are not integers
//2) from==to or from==to-1 (also in this latter case there is no need to move)
//3) from or to are lower than zero or greater than the array length
//in any other case, returns to
//Array.prototype.move = function(from, to){
//    var pInt = parseInt;
//    if(pInt(from)!==from || pInt(to)!==to){
//        return from;
//    }
//    var len = this.length;
//    if((from<0 || from>len)||(to<0 || to>len)){
//        return from;
//    }
//    //if we moved left to right, the insertion index is actually
//    //newIndex-1, as we must also consider to remove the current index markerIndex, so:
//    if(to>from){
//        to--;
//    }
//    if(from != to){
//        var elm = this.splice(from,1)[0];
//        this.splice(to,0,elm);
//        return to;
//    }
//    return from;
//}

function foldInfoBlocks() {
    var $J = jQuery;
    var extra = $J('.extraInfos');
    extra.find('.folded dl, .folded table').css('display', 'none');
    extra.find('a').click(function() { 
        $J(this).parents('.extraInfos').children().toggleClass('folded').find('dl, table').toggle(100);
        return false; 
    });
}
//returns the full path of the current url location removing the last slash '/' followed by one or more '#', if any
function urlNormalized(){
    var sPath = window.location.href;
    sPath = sPath.replace(/\/#*$/,"");
    return sPath;
}

/**
 * Global telemeta function to set the current selected menu active according toi the current url
 */
function setSelectedMenu(){
    var $J = jQuery;
    var menus = $J('#menu a');
    //build collections/items from http:/site/collections/items,
    //being http:/site/ = window.location.origin
    
    //function for normalizing paths (removes last n occurrences of the slash)
    var normalize = function(str){
        return str.replace(/\/+#*$/,"");
    }
    
    var host = window.location.host;
    var protocol = window.location.protocol
    var href = normalize(window.location.href);
     
    if(!(host) || !(protocol) || !(href)){
        return;
    }

    //var pageOrigin = normalize(window.location.origin); //does not exist in FF, so:
    var pageOrigin = normalize(protocol+"//"+host);
    var pageHref = normalize(href);

    menus.each(function(){
        ///if we are at home, the window location href corresponds to window location origin,
        //so we select only links whose link points EXACTLY to the origin (home link)
        var linkHref = normalize(this.href);
        var elm = $J(this);
        if(pageOrigin===pageHref){
            if(pageHref == linkHref){
                elm.addClass('active');
            }else{
                elm.removeClass('active');
            }
        }else{
            //here, on the other hand, we select if a link points to a page or super page
            //of the current page
            if(linkHref!=pageOrigin && pageHref.match("^"+linkHref+".*")){
                elm.addClass('active');
            }else{
                elm.removeClass('active');
            }
        }
        
    })
}

$(document).ready(function() {
    foldInfoBlocks();
    setSelectedMenu();
});

//****************************************************************************
//json(param, method, onSuccesFcn(data, textStatus, jqXHR), onErrorFcn(jqXHR, textStatus, errorThrown))
//global function to senbd/retrieve data with the server
//
//param: the data to be sent or retrieved.
//  param will be converted to string, escaping quotes newlines and backslashes if necessary.
//  param can be a javascript string, boolean, number, dictionary and array.
//      If dictionary or array, it must contain only the above mentioned recognized types.
//      So, eg, {[" a string"]} is fine, {[/asd/]} not
//
//method: the json method, eg "telemeta.update_marker". See base.py
//
//onSuccesFcn(data, textStatus, jqXHR) OPTIONAL --IF MISSING, NOTHING HAPPENS --
//   A function to be called if the request succeeds with the same syntax of jQuery's ajax onSuccess function.
//   The function gets passed three arguments 
//      The data returned from the server, formatted according to the dataType parameter;
//      a string describing the status;
//      and the jqXHR (in jQuery 1.4.x, XMLHttpRequest) object
//
//onErrorFcn(jqXHR, textStatus, errorThrown) OPTIONAL. --IF MISSING, THE DEFAULT ERROR DIALOG IS SHOWN--
//    A function to be called if the request fails with the same syntax of jQuery ajax onError function..
//    The function receives three arguments:
//      The jqXHR (in jQuery 1.4.x, XMLHttpRequest) object,
//      a string describing the type of error that occurred and
//      an optional exception object, if one occurred.
//      Possible values for the second argument (besides null) are "timeout", "error", "abort", and "parsererror".
//****************************************************************************

var json = function(param,method,onSuccessFcn,onErrorFcn){
    //this function converts a javascript object to a string
    var toString_ = function(string){
        if(typeof string == "string"){
            //escapes newlines quotes and backslashes
            string = string.replace(/\\/g,"\\\\")
            .replace(/\n/g,"\\n")
            .replace(/"/g,"\\\"");
        }
        var array; //used for arrays and objects (see below)
        if(typeof string == "boolean" || typeof string== "number" || typeof string == "string"){
            string = '"'+string+'"';
        }else if(string instanceof Array){
            array = [];
            for(var i = 0;i <string.length ; i++){
                array.push(toString_(string[i])); //recursive invocation
            }
            string='[';
            string+=array.join(",");
            string+=']';
        }else{
            array = [];
            for(var k in string){
                array.push(toString_(k)+":"+toString_(string[k])); //recursive invocation
            }
            string='{';
            string+=array.join(",");
            string+='}';
        }
        return string;
    };
    //var g = 9;
    //creating the string to send. We use array join and string concatenation with +=
    //as it is more efficient
    var param2string = toString_(param);
    var data2send = '{"id":"jsonrpc", "params":';
    data2send+=param2string;
    data2send+=', "method":"'
    data2send+=method;
    data2send+='","jsonrpc":"1.0"}';
    //        var data2send = '{"id":"jsonrpc", "params":[{"item_id":"'+ s(itemid)+
    //            '", "public_id": "'+s(marker.id)+'", "time": "'+s(offset)+
    //            '", "author": "'+s(marker.author)+
    //            '", "title": "'+s(marker.title)+
    //            '","description": "'+s(marker.desc)+'"}], "method":"'+method+'","jsonrpc":"1.0"}';
    var $J = jQuery;
    $J.ajax({
        type: "POST",
        url: '/json/',
        contentType: "application/json",
        data: data2send,
        dataType: "json",
        success: function(data, textStatus, jqXHR){
            if(onSuccessFcn){
                onSuccessFcn(data, textStatus, jqXHR);
            }
        },
        error: function(jqXHR, textStatus, errorThrown){
            if(onErrorFcn){
                onErrorFcn(jqXHR, textStatus, errorThrown);
                return;
            }
            //default:
            var details = "\n(no further info available)";
            if(jqXHR) {
                details="\nThe server responded witha status of "+jqXHR.status+" ("+
                jqXHR.statusText+")\n\nDetails (request responseText):\n"+jqXHR.responseText;
            }
            alert("ERROR: Failed to save"+details);
            
        }
    });

};
var uniqid = function() {
    var d = new Date();
    return new String(d.getTime() + '' + Math.floor(Math.random() * 1000000)).substr(0, 18);
};

var popup={
    _cfg_:{
        jQuery:jQuery,
        div: function(){
            var div = this.jQuery('<div/>').css({ //this is _cfg_
                position: 'absolute',
                overflow:'auto', //necessary to properly display the content
                display: 'none',
                border: '1px solid #e1e1e1',
                zIndex:1000
            });
            if(this.className){
                div.addClass(this.className);
            }
            return div;
        },
        className: 'component',
        //        mouseDownNamespace : "mousedown.popup__",
        //        keyDownNamespace : "keydown.popup__",

        //namespace: 'popup__', //used for namespaces when binding click to document
        handlersToRestore: [],
        event: null,
        divsToDelete:null,
        toggleBind: function(element, functionE){
            var clickNamespace = "click.popup__";
            var keydownNamespace =  "keyup.popup__";
            element.unbind(clickNamespace);
            element.unbind(keydownNamespace);
            if(functionE){
                element.bind(clickNamespace, functionE);
                element.bind(keydownNamespace,functionE);
            }
        }
    },
    
    isShowing: function(){
        return this._cfg_.divsToDelete ? true : false;
    },


    hide: function(){
        var toggleBind = this._cfg_.toggleBind;
       
        var $J = this._cfg_.jQuery;

        toggleBind($J(document));
        if(this._cfg_.divsToDelete){
            for(var i=0; i < this._cfg_.divsToDelete.length; i++){
                this._cfg_.divsToDelete[i].empty().remove();
            }
        }
        if(this._cfg_.event && this._cfg_.handlersToRestore){
            var type = this._cfg_.event.type; //which should be the same as h.type below, without namespaces?
            var invokerElement = this._cfg_.event.target;
            if(invokerElement){
                var e = $J(invokerElement);
                toggleBind(e);
                if(type){
                    //e.unbind(type);
                    for(var i=0; i<this._cfg_.handlersToRestore.length; i++){
                        var h = this._cfg_.handlersToRestore[i];
                        var functionCode = h.handler;
                        var namespace = ""+h.namespace;
                        if(namespace.length>0){
                            namespace="."+namespace;
                        }
                        var what = h.type+ namespace;
                        e.bind(what, functionCode);
                    }
                }
            }
        }
        this._cfg_.event=null;
        this._cfg_.handlersToRestore=null;
    },

    show:function(content, optionalEvent){
        consolelog("showing popup:"+optionalEvent);
        //if showing, hide
        if(this.isShowing()){
            this.hide();
        }

        var $J = this._cfg_.jQuery;
        var div = this._cfg_.div();
        //toggleBind sets the functions to hiding/keep shown the popup when clicking or
        //using the keyboard keys
        var toggleBind = this._cfg_.toggleBind;

        //remove the callback on invoker so that clicking on invoker does nothing
        //moreover, toggleBind on invoker so that clicking invoker doesn't hide the popup
        this.oldCallback = undefined;
        var oldHandlers=[];
        var invokerElement = optionalEvent && optionalEvent.target ? $J(optionalEvent.target) : undefined;
        if(invokerElement){
            optionalEvent.stopPropagation(); //othewrwise the popup hides immediately
            //cause the event is catched from the document click (added later, see below)
            // but apparently as soon as we add it it catches even the current event)
            var type = optionalEvent.type;
            var clickEvents =invokerElement.data("events")[type];
            $J.each(clickEvents, function(key, value) {
                oldHandlers.push(value);
            })
            invokerElement.unbind(type); //remove (temporarily) the binding to the event.
            //for instance, if we show the popup by clicking invoker, when the popup is shown do nothing
            //on clicking invoker until popup.hide is called
            toggleBind(invokerElement,function(e){ //add bindings to stop cancel the popup in case the invoker is clicked again
                e.stopPropagation();
                return false;
            });
        }
        //store the functions removed from invoker, if any, to restore them in this.hide
        this._cfg_.handlersToRestore = oldHandlers;
        this._cfg_.event = optionalEvent;
        
        //toggleBind on each child of content so that clicking and pressing keys on
        //a child doesn't hide the popup
        var children = $J(content).find('*');
        $J(children).each(function(){
            toggleBind($(this),function(e){
                e.stopPropagation();
                return false;
            });
        });
        //showing
        var doc = $J(document);
        $J('body').append(div);
        
        content.css('position','static'); //this is really important to place the content in the normal flow
        //within the div. static is the default
        content.show(); //in case the div is display:none
        div.append(content);

        //positioning div: center of the screen if no invoker, below the invoker otherwise
        var wdow = $J(window); //reference the window object (doing it once speeds up a bit performances)
        var windowH = wdow.height();
        var windowW = wdow.width();
        var position = div.offset();
        var shadowOffset=5;
        var size = {
            width:div.outerWidth(true)+shadowOffset,
            height:div.outerHeight(true)+shadowOffset
        };
        if(invokerElement){
            position = invokerElement.offset();
            position.top+=  invokerElement.outerHeight(true);
        }else{
            position.top = wdow.scrollTop()+ (windowH-size.height)/2;
            position.left = wdow.scrollLeft()+(windowW-size.width)/2;
        }
        //position div. This must be done immediately cause here below we want to get the div  offset
        //(div position in absolute - ie, document's - coordinates)
        div.css({
            'top': position.top,
            'left': position.left,
            'right': 'auto', //in case right has been set by some css class rule
            'bottom': 'auto' //see above...
        });
        //set the maximum size
        //due to overflow:auto a scrollbar will automatically appear
        var max = Math.max; //reference max immediately (speeds up performances a bit)
        var maxSize = {
            width: max(20,windowW +  wdow.scrollLeft() -position.left-shadowOffset),
            height: max(20, (windowH + wdow.scrollTop() -position.top- shadowOffset))
        }
        //position div and size:
        var divPadding = {
            left: div.outerWidth()-div.width(),
            top:div.outerHeight()-div.height()
        }; //setting width on a div means the width(),
        //but calculations here are made according to outerWidth(true), so we need this variable (se below)

        //the shadow in the background will be created according to the actual div size
        //However, since we do not specify neither width nor height, the calculation of the div size
        //works if maxWidth and maxHeight do set a width and height. In order to do so, they
        //must be lower or equal to the actual div width and height. That's why the "min" here below:'
        div.css({
            'maxWidth': Math.min(div.width(), maxSize.width-divPadding.left),
            'maxHeight': Math.min(div.height(), maxSize.height-divPadding.top)
        });

        //last thing: if invoker element exist, set width at least invoker element width
        if(invokerElement){
            var iEw = invokerElement.outerWidth(); //no margins considered
            if(iEw<maxSize.width && iEw>div.outerWidth()){
                div.css({
                    'minWidth':iEw-divPadding.left
                });
            }
        }
        //now we can build the divShadow
        var divShadow = div.clone(false,false).empty().css({
            'zIndex':999,
            'borderColor':'#000',
            'display':'none',
            'backgroundColor':'#000'
        }).insertAfter(div);
        //store the divs to be removed
        this._cfg_.divsToDelete = [div,divShadow];
        //add a listener to the document. If one of the content children is clicked/keypressed,
        //we won't come here. Otherwise hide popup
        var me = this;
        var hide = this.hide;
        toggleBind(doc,function(e){
            hide.apply(me);
            e.stopPropagation();
        });
        div.show(300, function(){ //basically in between fast (200) and slow (600)
            //position div shadow:
            divShadow.show();
            consolelog(div.outerHeight(true)+" "+div.outerHeight(false));
            consolelog(divShadow.outerHeight(true)+" "+divShadow.outerHeight(false));
            
            //set focus to the first input component, if any. Otherwise try with anchors, otherwise do nothing
            var inputs = $J(div).find(':input');
            if(inputs && inputs[0]){
                inputs[0].focus();
            }else{
                inputs = $J(div).find('a');
                if(inputs && inputs[0]){
                    inputs[0].focus();
                }
            }

            divShadow.fadeTo(0,0.4, function(){
                divShadow.css({
                    'top': (position.top+shadowOffset),
                    'left': (position.left+shadowOffset),
                    'width': div.outerWidth(true),
                    'height': div.outerHeight(true)
                });

            });
        });
        return false; //to avoid scrolling if we clicked on an anchor
    },

    //field must be a dictionary of label:defaultValues (both strings)
    //callbackOnOk is the callback to be executed on ok, if null ok will simply hide the dialog
    createDivDialog : function(field,callbackOnOk){

        var $J = this._cfg_.jQuery;
        var table = $J('<table/>');
        var fieldElms = {};
        for(var label in field){
            var input = $('<input/>')
            .attr('type','text').val(field[label]).attr("name",label);
            table.append($J('<tr/>')
                .append($J('<td/>').html(label))
                .append($J('<td/>').append(input)));
            fieldElms[label]=input;
        }

        var p = this;
        var onCancel= function(){
            p.hide();
            return false;
        };
       
        var onOk= function(){
            if(callbackOnOk){
                var ret = {};
                var inputs = table.find("input");
                $J.each(inputs, function(key,value){
                    var v = $J(value);
                    ret[v.attr('name')] = v.val();
                });
                callbackOnOk(ret);
                return false;
            }else{
                return onCancel();
            }
        };
        var subdiv = $J('<div/>').css({
            'padding':'1ex',
            'float':'right'
        }).
        append(
            $J('<a/>').
            html('Ok').
            addClass('component_icon').
            addClass('button').
            addClass('icon_ok').
            attr('href','#').
            click(function(){
                return onOk();
            })
            );
        if(callbackOnOk){
            subdiv.append(
                $J('<a/>').
                html('Cancel').
                addClass('component_icon').
                addClass('button').
                addClass('icon_cancel').
                attr('href','#').
                click(function(){
                    return onCancel();
                })
                );
        }
        //popupDialog(element,table,onOk);
        return $J('<div/>').append(table).append(subdiv);
    }
}

/**
 * Loads scripts asynchronously
 * can take up to four arguments:
 * root (optional): a string specifying the root (such as '/usr/local/'). Must end with slash, otherwise
 *      each element in scriptArray must begin with a slash
 * scriptArray: a string array of js script filenames, such as ['script1.js','script2.js']
 * callback (optional): callback to be executed when ALL scripts are succesfully loaded
 * loadInSeries (optional): if true scripts are loaded in synchronously, ie each script is loaded only once the
 *      previous has been loaded. The default (argument missing) is false
 *
 * Examples. Given scripts = ['s1.js', 's2.js']
 *  loadScripts(scripts)                          //loads (asynchronously) scripts
 *  loadScripts('/usr/', scripts)                 //loads (asynchronously) ['/usr/s1.js', '/usr/s2.js']
 *  loadScripts(scripts, callback)                //loads (asynchronously) scripts. When loaded, executes callback
 *  loadScripts('/usr/', scripts, callback)       //loads (asynchronously) ['/usr/s1.js', '/usr/s2.js']. When loaded, executes callback
 *  loadScripts(scripts, callback, true)          //loads (synchronously) scripts. When loaded, executes callback
 *  loadScripts('/usr/', scripts, callback, true) //loads (synchronously) ['/usr/s1.js', '/usr/s2.js']. When loaded, executes callback
 *
 */
function loadScripts(){
    var optionalRoot='', scriptArray=[], callback=undefined, loadInSeries=false;
    var len = arguments.length;
    if(len==1){
        scriptArray = arguments[0];
    }else if(len==2){
        if(typeof arguments[0] == 'string'){
            optionalRoot = arguments[0];
            scriptArray = arguments[1];
        }else{
            scriptArray = arguments[0];
            callback = arguments[1];
        }
    }else if(len>2){
        if(typeof arguments[0] == 'string'){
            optionalRoot = arguments[0];
            scriptArray = arguments[1];
            callback = arguments[2];
            if(len>3){
                loadInSeries = arguments[3];
            }
        }else{
            scriptArray = arguments[0];
            callback = arguments[1];
            loadInSeries = arguments[2];
        }
    }
    
    if(!scriptArray){
        if(callback){
            callback();
        }
        return;
    }
    len = scriptArray.length;
    var i=0;
    if(optionalRoot){
        for(i =0; i<len; i++){
            scriptArray[i] = optionalRoot+scriptArray[i];
        }
    }

    var $J = jQuery;
    //var time = new Date().getTime();
    if(loadInSeries){
        var load = function(index){
            if(index<len){
                //consolelog("loading "+scriptArray[index]+" "+new Date().getTime());
                $J.getScript(scriptArray[index],function(){
                    load(index+1);
                });
            }else if(callback){
                //consolelog("EXECUTING CALLBACK ELAPSED TIME:"+(new Date().getTime()-time));
                callback();
            }
        };
        load(0);
    }else{
        var count=0;
        var s;
        for(i=0; i <len; i++){
            s = scriptArray[i];
            //consolelog("loading "+s+" "+new Date().getTime());
            $J.getScript(s, function(){
                count++;
                if(count==len && callback){
                    //consolelog("EXECUTING CALLBACK ELAPSED TIME:"+(new Date().getTime()-time));
                    callback();
                }
            });
        }
    }
}

function consolelog(text){
    if(typeof console != 'undefined'){
        var c = console;
        if (c.log) {
            c.log(text);
        }
    }
}

function PopupUtils(){
    var $J= jQuery;
    var wdow = $J(window); //reference the window object (doing it once speeds up a bit performances)
    var doc = $J(document);
    var screenRect = function(){
        return {
            x:wdow.scrollLeft(),
            y:wdow.scrollTop(),
            width:wdow.width(),
            height:wdow.height()
        };
    };
    

    /**
     * sets dialogDiv (a jQuery object or a DivDialog, see below) as popup mode. In other words,
     * scans each sub-element of dialogDiv and assigns to it a onblur event: when the subselemnt looses the focus and the focus
     * is NOT given to another dialogDiv subelement, hides or removes (depending on removeOnHide param) dialogDiv.
     * The workaround is quite tricky and maybe not well formed, as it uses a timeout function. However, any other implementation was trickier
     * and with potential drawbacks. Note that any subelement of dialogDiv is assigned a "focus" attribute with the current time in millisecs
     */
//    var setAsPopup = function(dialogDiv, removeOnHide){
//        dialogDiv.setAsPopup(removeOnHide ? function(){dialogDiv.remove();} : function(){dialogDiv.hide();});
//    };

    this.bindClickToPopup = function(invokerAsJQueryObj, popupContent){
     var p = new DivDialog(popupContent);
        var oldShow = p.show;
       // var pint = parseInt;
        p.show = function(){

            var rect = screenRect();
            var offs = invokerAsJQueryObj.offset();
            var height = invokerAsJQueryObj.outerHeight();

            var spaceAbove = offs.top - rect.y;
            var spaceBelow = rect.height - height - spaceAbove;

            consolelog('wHeight:'+rect.height+ ' space above: '+spaceAbove + ' spacebelow: '+spaceBelow);

            if(spaceAbove>spaceBelow){
                p.css({'maxHeight':(spaceAbove-p.shadowoffset)+'px', 'top':rect.y+'px'});
            }else{
                p.css({'maxHeight':(spaceBelow-p.shadowoffset)+'px', 'top':(offs.top+height)+'px'});
            }
            p.css({'height':'auto','width' :'auto', 'maxWidth': (rect.x+rect.width-offs.left)+'px'});

        //consolelog("size"); consolelog(size);
//        p.offset({
//            left: rect.x + pint((rect.width-size.width)/2),
//            top: rect.y + pint((rect.height-size.height)/2)
//        });
        //consolelog("offset"); consolelog({
        //    left: rect.x + pint((rect.width-size.width)/2),
        //    top: rect.y + pint((rect.height-size.height)/2)
       // });

            oldShow.apply(p,arguments);
            p.refreshShadowPosition();
            p.setFocus();
        };
        consolelog(invokerAsJQueryObj);
        p.css({
            'minWidth':invokerAsJQueryObj.outerWidth()+'px',
            'left':invokerAsJQueryObj.offset().left+'px'
        });

        p.setPopupFocus(function(){p.hide();});

        invokerAsJQueryObj.unbind('click').click(function(evt){
           p.show();
           return false;
        });
        //p.show();
        //p.setFocus();
    }
    /**
     * Shows an info dialog centered in screeen. The dialog is a DivDialog with maxwidth and maxheight equals to the half of the
     * visible window width and height, respectively. Content can be a jQuery object (ie an array of html elements) or a string
     * denoting the innerHTML of the dialog div. timeInMsec can be:
     * a number (in msec) specifying after how much time the dialog will be removed (for fast messages)
     * the string 'hide' to specify that the div will be hidden when it looses focus
     * the string 'remove' to specify that the div will be removed when it looses the focus
     *
     */
    this.showInfoDialog = function(content, timeInMsec){
        var p = new DivDialog(content);
        var oldShow = p.show;
        var pint = parseInt;
        p.show = function(){
            oldShow.apply(p,arguments);
            var rect = screenRect();
//        var pint = parseInt;
//        p.css({
//            'maxWidth':pint(rect.width/2)+'px',
//            'maxHeight':pint(rect.height/2)+'px'
//        });
//consolelog("screeenrect"); consolelog(rect);
        var size = p.size();
        //consolelog("size"); consolelog(size);
        p.offset({
            left: rect.x + pint((rect.width-size.width)/2),
            top: rect.y + pint((rect.height-size.height)/2)
        });
        //consolelog("offset"); consolelog({
        //    left: rect.x + pint((rect.width-size.width)/2),
        //    top: rect.y + pint((rect.height-size.height)/2)
       // });

        p.refreshShadowPosition();

        };
        var rect = screenRect();
        p.css({
            'maxWidth':pint(rect.width/2)+'px',
            'maxHeight':pint(rect.height/2)+'px'
        });
        
        if(typeof timeInMsec == 'number'){ //set a timeout
            setTimeout(function(){
                p.remove();
                p=null;
            },timeInMsec);
        }else if(timeInMsec == 'hide'){ //is a boolean
            p.setPopupFocus(function(){p.hide();});
        }else if(timeInMsec == 'remove'){ //is a boolean
            p.setPopupFocus(function(){p.remove();});
        }
        p.show();
        p.setFocus();
    };
}

//content: string or jQueryElement
//type 'popup',
//DivDialog(content,type,attributes)

var pppUtils = new PopupUtils();
function DivDialog(content){
    var $J = jQuery;
    var doc = $J(document);
    var firstFocusableElement = undefined; //set in focusout
    var className = 'component';
    var basecss = {
        'position':'absolute',
        'display':'none'
    };
    var popup = $J('<div/>').addClass(className).css(basecss).css({
        'zIndex':1000
    });
    var popupContent = $J('<div/>').css({
        'overflow':'auto'
    });
    
    var popupshadow = popup.clone(true,true).removeAttr('id').empty().css({
        'backgroundColor':'#000',
        'border':'0px',
        'zIndex':900,
        'margin':'0px',
        'padding':'0px'
    }).fadeTo(0,0.4);
    var both = popup.add(popupshadow);


    if(content){
        if(content instanceof $J){
            popupContent.empty().append(content);
        }else{
            popupContent.html(content);
        }
    }
    popup.append(popupContent);



//    if(invoker.is('a') || invoker.is('input[type=button]') || invoker.is('button') ||
//    invoker.is('input[type=submit]')){
//        var w = invoker.outerWidth();
//        popup.css({'minWidth':w+'px'});
//        this.show = show1();
//    }else{
//
//    }

    this.maxSize = function(size){
        popup.css({'maxHeight':size.height,'maxWidth':size.width});
        popupContent.css({'maxHeight':size.height-(popup.outerHeight()-popup.height()),'maxWidth':size.width-(popup.outerWidth()-popup.width())});
    };
    this.minsize = function(size){
        popup.css({'minHeight':size.height,'minWidth':size.width});
    };
     this.offset = function(){
        var ret = popup.offset.apply(popup,arguments);
        //refreshPosition();
        return me;
    };

    //function (private) to refresh shadow position
    this.shadowoffset = 5;
    this.size = function(){
        return {
            width: popup.outerWidth(),
            height:popup.outerHeight()
        };
    };



    this.refreshShadowPosition = function(){
        if(!popup.is(":visible")){
            popupshadow.hide(); //to be sure
            return;
        }else{
            popupshadow.show();
        }
        var offs = popup.offset();
        offs.top+=this.shadowoffset;
        offs.left+=this.shadowoffset;
        popupshadow.offset(offs);
        popupshadow.css({
            'width':popup.outerWidth()+'px',
            'height':popup.outerHeight()+'px'
        });
        popupContent.css({
            'maxWidth': (parseInt(popup.css('maxWidth')) -(popupContent.outerWidth()-popupContent.width())) +'px',
            'maxHeight':(parseInt(popup.css('maxHeight'))-(popupContent.outerHeight()-popupContent.height()))+'px'
        });
    };

    //dummy overriding of some jquery functions
    var me = this;
    this.remove = function(){
        both.empty();
        both.remove.apply(both,arguments);
        return me;
    };
    this.find = function(){
        return popupContent.find.apply(popupContent,arguments);
    };
    this.hide = function(){
        return both.hide.apply(both,arguments);
        return me;
    };
    
    this.show = function(){
        if(!(popup.parent().length)){
            $J('body').append(both);
        }
        var ret = popup.show.apply(popup,arguments);
        //refreshPosition();
        return me;
    };

    this.setFocus = function(){
        if(firstFocusableElement && firstFocusableElement.parent().length && firstFocusableElement.is(':visible')){
            firstFocusableElement.focus();
        }
    }
    //popup specific functions

    //set css: note that margin position and zIndex will be overridden
    this.css = function(){
        var arg = arguments;
        if(arguments.length==2){ //setting a single css element
            if(arguments[0] == 'margin' || arguments[0] == 'position' || arguments[0] == 'zIndex'){
                return me;
            }
        }else if(arguments.length==1){  //single argument
            if(typeof arguments[0] == 'string'){
                return popup.css(arguments[0]);
            }else{
                var a = arguments[0];
                for(var k in a){
                    if(k == 'margin' || k == 'position' || k == 'zIndex'){
                        delete a[k];
                    }
                }
                arg = [a];
//                consolelog('css');
//                consolelog(arg);
            }
        }else{
            return me;
        }
        var ret = popup.css.apply(popup,arg);
        //refreshPosition();
        return me;
    };



//    this.bindAsPopupFor = function(jQueryAnchorElement){
//        if(!jQueryAnchorElement.attr('id')){
//            jQueryAnchorElement.attr('id','popup_'+new Date().getTime());
//        }
//        var id = jQueryAnchorElement.attr('id');
//
//        anchorElement.click(function(){
//
//        })
//
//    }
   
    this.setPopupFocus = function(callbackOnFocusLost){
        
        //find all foccusable elements
        var elementsWithFocus = $J(popupContent).find('textarea,a,input');
        //focus must be given also to the containing popup beacuse
        //if a scrollbar is present, moving the scrollbar sets the focus to popup (not popupContent. So
        //apparently even if the scrollbar is caused by css 'popupContent.scroll=auto', it's like if it was
        //'part' of the parent container popup)
        //TODO: TEST IT WITH OTHER BROWSERS!!!! if not working, manda tutto affanculo and use click events
        popup.attr('tabindex',1);
        elementsWithFocus = elementsWithFocus.add(popup);
        //build the attribute focus to recognize subelement of popup
        var focusid = 'popupfocus'+(new Date().getTime());
        //bind the blur to each focusable element:
        elementsWithFocus.each(function(i,e){
            var ee = $J(e);
            ee.attr(focusid,'true');
            ee.blur(function(){
                //wait 250msec to see if the focus has been given to another popup focusable element: if yes, do nothing
                //otherwise execute callback
                setTimeout(function(){
                    var v = document.activeElement;
                    consolelog(v);
                    if(v && $J(v).attr(focusid)){
                        return;
                    }
                    callbackOnFocusLost();
                },200)
            }); //set here another time delay. 300 seems to be the good compromise between visual hide and safetiness that
        //meanwhile the focus has already been given to the next component
        });
        //set the first focusable element
        firstFocusableElement = $J(elementsWithFocus[0]);
    };
   
    this.attr = function(){
        var ret =  popup.attr.apply(popup,arguments);
        //refreshPosition();
        return me;
    };
    this.html = function(){
        if(arguments.length==0){
            return popupContent.html();
        }
        var ret = popupContent.html.apply(popup,arguments);
        //refreshPosition();
        return me;
    }
    this.append = function(){
        var ret = popupContent.append.apply(popup,arguments);
        //refreshPosition();
        return me;
    }
}


