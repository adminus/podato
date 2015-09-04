const flux = require("../flux");
const PodcastActions = require("../actions/podcast-actions");
var popular_podcasts = [];

const PopularPodcastsStore = flux.createStore(class PopularPodcastsStore {
    constructor(){
        this.popularPodcasts = [];
        this.bindActions(PodcastActions);
    }

    get(){
        return this.popularPodcasts
    }

    onFetchPopularPodcasts(podcasts){
        this.popularPodcasts = podcasts;
    }
}, "PopularPodcastsStore");

module.exports = PopularPodcastsStore;
