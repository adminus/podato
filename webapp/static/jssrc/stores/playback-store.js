const flux = require("../flux");
const PlaybackActions = require("../actions/playback-actions");

const PlaybackStore = flux.createStore(class UsersStore{
    constructor(){
        this.currentEpisode = null;
        this.playing = false;
        this.duration = 0;
        this.currentTime = 0;
        this.bindActions(PlaybackActions);
    }

    onPlayEpisode(episode){
        this.currentEpisode = episode;
        this.playing = true;
    }

    onPause(){
        this.playing = false;
    }

    onResume(){
        this.playing = true;
    }

    onTimeUpdate(playback){
        this.currentTime = playback.getCurrentTime();
        this.duration = playback.getDuration();
    }
}, "PlaybackStore");

module.exports = PlaybackStore;
