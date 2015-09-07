const flux = require("../flux");
const PlaybackActions = require("../actions/playback-actions");

const PlaybackStore = flux.createStore(class UsersStore{
    constructor(){
        this.currentEpisode = null;
        this.currentEpisode = null;
        this.playing = false;
        this.playbackState = {};
        this.bindActions(PlaybackActions);
    }

    onPlayEpisode(episode){
        this.currentEpisode = episode;
        this.playing = true;
    }
}, "UsersStore");

module.exports = PlaybackStore;
