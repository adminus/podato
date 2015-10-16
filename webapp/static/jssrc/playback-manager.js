var merge = require("merge");
var EventEmitter = require("eventemitter3");

const PlaybackManager = new EventEmitter()

merge(PlaybackManager, {
    episode: null,
    audio: new Audio(),
    init(){
        this.audio.ontimeupdate = this.emit.bind(this, "time", this);
        this.audio.onprogress = this.emit.bind(this, "load", this);
        this.audio.onended = this.emit.bind(this, "ended", this);
    },
    setEpisode(ep){
        this.episode = ep;
        this.audio.src = ep.enclosure.url;
    },
    play(){
        this.audio.play();
    },
    pause(){
        this.audio.pause()
    },
    seek(secs){
        this.audio.currentTime = secs;
    },
    getCurrentTime(){
        return this.audio.currentTime;
    },
    getDuration(){
        return this.audio.duration;
    }
});

PlaybackManager.init();

module.exports = PlaybackManager;
