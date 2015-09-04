const flux = require("../flux");
const PodcastActions = require("../actions/podcast-actions");

var podcasts = {}

const PodcastsStore = flux.createStore(class PodcastsStore {
    constructor(){
        this.podcasts = {}
        this.bindActions(PodcastActions);
    }

    static getPodcast(id){
        return this.state.podcasts[id]
    }

    onFetchPodcast(podcast){
        this.podcasts[podcast.id] = podcast;
    }
}, "PodcastsStore");

module.exports = PodcastsStore;
