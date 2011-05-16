/**
 * TimeSide - Web Audio Components
 * Copyright (c) 2008-2009 Samalyse
 * Author: Olivier Guilyardi <olivier samalyse com>
 * License: GNU General Public License version 2.0
 */

TimeSide(function($N) {

    $N.Class.create("SoundProvider", $N.Core, {
        sound: null,
        timer: null,
        buggyPosition: null,
        isDurationForced: false,
        state: {
            position: null,
            duration: null,
            playing: false,
            buffering: false
        },
        lastState: null,

        initialize: function($super, cfg) {
            $super();
            this.configure(cfg, {
                source: null,
                duration: null
            });
            this.sound = this.cfg.source;
            if (this.cfg.duration) {
                this.forceDuration(this.cfg.duration);
            }
            this.state.position = 0;
            this.update = this.attach(this._update);
            this.timer = setInterval(this.update, 43);
            this.init=true;
            this._update();
            this.init=false;
        },

        free: function($super) {
            this.sound = null;
            $super();
        },

        play: function() {
            if (this.sound) {
                //it seems that, if sound is played until its end
                //playing sound again resets the volume to 100, even though
                //sound.volume is at the right value. We use this trick which seems to work:
                this.sound.setVolume(this.sound.volume);
                if (!this.sound.playState) {
                    this.sound.play();
                    //console.log(this.getVolume());
                } else if (this.sound.paused) {
                    this.sound.resume();
                }
            }
            return this;
        },

        pause: function() {
            if (this.sound){
                this.sound.pause();
            }
            return this;
        },

        setVolume: function(volume) {
            if(typeof volume != 'number'){
                return this;
            }
            volume = volume<0 ? 0 : volume >100 ? 100 : parseInt(volume);
            if (this.sound && this.sound.volume!==volume){
                this.sound.setVolume(volume);
            }
            this.fire('volume',{'volume':volume});
            return this;
        },

        getVolume: function() {
             return this.sound.volume;
        },

        seek: function(offset) {
            if (this.sound) {
                this.sound.setPosition(offset * 1000);
                if (!this.state.playing) {
                    //it's not always a number. When not playing it is a string
                    //(sound manager?)
                    var offs = typeof offset == "number" ? offset : parseFloat(offset);
                    this.buggyPosition = this.sound.position / 1000;
                    this.state.position = offs;
                }
            }
            return this;
        },

        isPlaying: function() {
            return this.state.playing;
        },

        getPosition: function() {
            if (this.state.position == null){
                this._retrieveState();
            }
            return this.state.position;
        },

        getDuration: function() {
            if (this.state.duration == null){
                this._retrieveState();
            }
            return this.state.duration;
        },

        forceDuration: function(duration) {
            this.state.duration = duration;
            this.isDurationForced = true;
        },

        isBuffering: function() {
            return this.state.buffering;
        },

        _retrieveState: function() {
            if (this.sound) {
                this.state.playing = (this.sound.playState && !this.sound.paused);
                if (this.state.playing) {
                    var position = this.sound.position / 1000;
                    if (position != this.buggyPosition) {
                        this.state.position = position;
                        this.buggyPosition = null;
                    }
                }
                if (!this.isDurationForced) {
                    if (this.sound.readyState == 1) {
                        this.state.duration = this.sound.durationEstimate / 1000;
                    } else {
                        this.state.duration = this.sound.duration / 1000;
                    }
                }
                this.state.buffering = (this.sound.readyState == 1 && this.state.position > this.sound.duration / 1000);
            }
        },

        _update: function() {
            this._retrieveState();
            var updated = false;
            var k;
            if (this.lastState) {
                for (k in this.state) {
                    if (this.state[k] != this.lastState[k]) {
                        updated = true;
                        break;
                    }
                }
            } else {
                this.lastState = {};
                updated = true;
            }
            if (updated) {
                var fireevent = false;
                for (k in this.state) {
                    if(k=='position' && this.lastState[k]!==undefined && this.lastState[k]!=this.state[k]){
                        //this.lastState[k]!==undefined because otherwise we are initializing
                        this.debug('fire-play-stop');
                        fireevent = true;
                    }else if(k=='playing' && this.lastState[k] && !this.state[k]){
                        //stop playing, fire again to move the cursor REALLY at the end
                        this.debug('fire-stop');
                        fireevent = true;
                    }
                    if(this.state[k] != this.lastState[k]){
                        this.debug('(soundprovider _update) '+k+': oldVal: '+this.lastState[k]+': val: '+this.state[k]);
                    }
                    this.lastState[k] = this.state[k];
                    
                }
                if(fireevent){
                    this.debug('firing');
                    this.fire('update');
                }
            }
        },

        setSource: function(source) {
            this.debug("setting source");
            this.sound = source;
            return this;
        }

    });

    $N.notifyScriptLoad();

});