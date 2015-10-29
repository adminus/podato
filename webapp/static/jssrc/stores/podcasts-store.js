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
        this.podcasts[podcast.id].episodes_page = 1;
    }

    onFetchEpisodes(payload){
        const podcast = this.podcasts[payload.podcastId];
        podcast.episodes = podcast.episodes.concat(payload.result.episodes);
        podcast.episodes_page += 1;
        podcast.has_more_episodes = payload.result.has_more_episodes;
        console.log("received episodes: ");
        console.log(payload);
    }
}, "PodcastsStore");

module.exports = PodcastsStore;
