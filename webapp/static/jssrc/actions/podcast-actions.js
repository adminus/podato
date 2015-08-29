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
                    if(resp.obj.success == true){
                        PodcastActions.fetchSubscriptions("me")
                        resolve({
                            actionType: constants.actionTypes.SUBSCRIBED,
                            podcasts: podcastIds
                        });
                    }else if(resp.obj.success == false){
                        reject(resp);
                    }else{
                        if(!resp.obj.id){
                            reject({"errors":"response object has no success property, but no id either."})
                        }else{
                            PodcastActions.checkSubscriptionResult(resp.obj.id).then(()=>{
                                PodcastActions.fetchSubscriptions("me")
                                resolve({
                                    actionType: constants.actionTypes.SUBSCRIBED,
                                    podcasts: podcastIds
                                });
                            });
                        }
                    }
                });
            });
        });
    },
    checkSubscriptionResult(id){
        return new Promise((resolve, reject) => {
            console.log("Checking for subscription result "+id);
            api.loaded.then(()=>{
                api.subscriptionResults.getSubscriptionResult({resultId: id}, (resp) => {
                    console.log("subscription result:");
                    console.log(resp.obj);
                    if(resp.obj.success==true){
                        resolve({
                            actionType: constants.actionTypes.SUBSCRIBE_PROGRESS,
                            total: resp.obj.total,
                            progress: resp.obj.progress
                        })
                    }else if(resp.obj.success==false){
                        reject(resp);
                    }else{
                        PodcastActions.reportProgress(resp.obj.progress, res.obj.total);
                        PodcastActions.checkSubscriptionResult(id).then(resolve, reject);
                    }
                })
            });
        })
    },
    reportProgress(progress, total){
        return {
            actionType: constants.actionTypes.SUBSCRIBE_PROGRESS,
            total: resp.obj.total,
            progress: resp.obj.progress
        };
    },
    unsubscribe(podcastIds){
        if(podcastIds.constructor !== Array){
            podcastIds = [podcastIds];
        }
        heap.track("subscribe", {podcastIds: podcastIds.join(",")})
        return new Promise((resolve, reject) => {
            api.loaded.then(() => {
                api.users.unsubscribe({userId: "me", podcast: podcastIds}, (resp) => {
                    if (resp.obj.success){
                        resolve({
                            actionType: constants.actionTypes.UNSUBSCRIBED,
                            podcasts: podcastIds
                        });
                        PodcastActions.fetchSubscriptions("me");
                    }else{
                        reject(resp);
                    }
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
