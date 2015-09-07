var merge = require("merge");
var EventEmitter = require("events").EventEmitter;

const PlaybackManager = new EventEmitter()

merge(PlaybackManager, {
    episode: null,
    audio: new Audio(),
    setEpisode(ep){
        this.episode = ep;
        this.audio.src = ep.enclosure.url;
    },
    play(){
        this.audio.play();
        this._startTimeUpdates();
    },
    pause(){
        this._stopTimeUpdates();
        this.audio.pause()
    },
    seek(secs){
        this.audio.currentTime = secs;
    },
    getCurrentTime(){
        return this.audio.currentTime;
    },
    getDuration(){
        return this.audio.duration();
    },
    _startTimeUpdates(){
        this._timeUpdateId = setInterval(() => {
            this.emit("update", this._makeEventObj());
        }, 500);
    },
    _stopTimeUpdates(){
        clearInterval(this._timeUpdateId);
    },
    _makeEventObj(){
        return {
            duration: this.audio.duration,
            time: this.audio.currentTime
        }
    }
});

module.exports = PlaybackManager;
