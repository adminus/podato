const flux = require("../flux");
const api = require("../api");

const PlaybackManager = require("../playback-manager.js");

const PlaybackActions = flux.createActions(class UserActions {
    playEpisode(episode){
        PlaybackManager.setEpisode(episode);
        PlaybackManager.play();
        this.dispatch(episode);
    }

    pause(){
        PlaybackManager.pause();
        this.dispatch(true);
    }

    resume(){
        PlaybackManager.play();
        this.dispatch(true);
    }
});

module.exports = PlaybackActions;
