const flux = require("../flux");
const PodcastActions = require("../actions/podcast-actions");

var podcasts = {}

const PodcastsStore = flux.createStore(class PodcastsStore {
    constructor(){
        this.podcasts = {}
        this.bindActions(PodcastActions);
    }

    getPodcast(id){
        return this.podcasts[id]
    }

    onFetchPodcast(podcast){
        this.podcasts[podcast.id] = podcast;
    }
});

module.exports = PodcastsStore;
