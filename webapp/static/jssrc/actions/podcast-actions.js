const mcfly = require("../mcfly");
const api = require("../api");
const constants = require("../constants");

var transformPodcast = function(podcast){
    podcast.encoded_id = encodeURIComponent(podcast.id);
    return podcast;
}

const PodcastActions = mcfly.createActions({
    subscribe(podcastIds){
        if(podcastIds.constructor !== Array){
            podcastIds = [podcastIds];
        }
        heap.track("subscribe", {podcastIds: podcastIds.join(",")})
        return new Promise((resolve, reject) => {
            api.loaded.then(() => {
                api.users.subscribe({userId: "me", podcast:podcastIds}, (resp) => {
                    API.asyncResultToPromise(resp).then((result) => {
                        resolve({
                            actionType: constants.actionTypes.SUBSCRIBED,
                            podcasts: podcastIds
                        });
                    });
                });
            });
        });
    },
    unsubscribe(podcastIds){
        if(podcastIds.constructor !== Array){
            podcastIds = [podcastIds];
        }
        heap.track("subscribe", {podcastIds: podcastIds.join(",")})
        return new Promise((resolve, reject) => {
            api.loaded.then(() => {
                api.users.unsubscribe({userId: "me", podcast: podcastIds}, (resp) => {
                    API.asyncResultToPromise(resp).then((res) => {
                        resolve({
                            actionType: constants.actionTypes.UNSUBSCRIBED,
                            podcasts: podcastIds
                        });
                    });
                });
            });
        });
    },
    fetchPodcast(podcastId){
        return new Promise((resolve, reject) => {
            api.loaded.then(() => {
                api.podcasts.getPodcast({podcastId: podcastId}, (resp) => {
                    if(resp.status !== 200){
                        reject(resp.statusText);
                        return
                    }
                    resolve({
                        actionType: constants.actionTypes.PODCAST_FETCHED,
                        podcast: transformPodcast(resp.obj)
                    });
                });
            });
        });
    },
    fetchSubscriptions(userId){
        userId = userId || "me"
        PodcastActions.fetchingSubscriptions(userId);
        return new Promise((resolve, reject) => {
            api.loaded.then(() => {
                api.users.getSubscriptions({userId: userId}, (resp) => {
                    if(resp.status !== 200){
                        reject(resp.statusText);
                        return
                    }
                    resolve({
                        actionType: constants.actionTypes.SUBSCRIPTIONS_FETCHED,
                        userSubscriptions: resp.obj.map(transformPodcast),
                        userId: userId
                    })
                })
            });
        });
    },
    fetchingSubscriptions(userId){
        return {
            actionType: constants.actionTypes.FETCHING_SUBSCRIPTIONS,
            userId: userId
        }
    },
    fetchPopularPodcasts(){
        return new Promise((resolve, reject) => {
            api.loaded.then(() => {
                api.podcasts.query({order:"subscribers"}, (res) => {
                    resolve({
                        actionType: constants.actionTypes.POPULAR_PODCASTS_FETCHED,
                        podcasts: res.obj.map(transformPodcast)
                    });
                });
            });
        });
    }
});

module.exports = PodcastActions;
