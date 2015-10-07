const flux = require("../flux");
const PlaybackActions = require("../actions/playback-actions");

const PlaybackStore = flux.createStore(class UsersStore{
    constructor(){
        this.currentEpisode = null;
        this.playing = false;
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
}, "PlaybackStore");

module.exports = PlaybackStore;
