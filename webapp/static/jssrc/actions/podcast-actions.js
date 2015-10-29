const flux = require("../flux");
const api = require("../api");

var transformPodcast = (podcast) => {
    podcast.encoded_id = encodeURIComponent(podcast.id);
    return podcast;
}

const PodcastActions = flux.createActions(class PodcastActions {
    subscribe(podcastIds){
        if(podcastIds.constructor !== Array){
            podcastIds = [podcastIds];
        }
        heap.track("subscribe", {podcastIds: podcastIds.join(",")})
        return new Promise((resolve, reject) => {
            api.loaded.then(() => {
                api.users.subscribe({userId: "me", podcast: podcastIds}, (resp) => {
                    if(resp.obj.success == true){
                        this.actions.fetchSubscriptions("me");
                        this.dispatch(podcastIds);
                    }else if(resp.obj.success == false){
                        reject(resp);
                    }else{
                        if(!resp.obj.id){
                            reject({"errors":"response object has no success property, but no id either."})
                        }else{
                            this.actions.checkSubscriptionResult(resp.obj.id).then(()=>{
                                this.actions.fetchSubscriptions("me")
                                this.dispatch(podcastIds);
                            });
                        }
                    }
                });
            });
        });
    }

    checkSubscriptionResult(id){
        return new Promise((resolve, reject) => {
            console.log("Checking for subscription result "+id);
            api.loaded.then(()=>{
                api.subscriptionResults.getSubscriptionResult({resultId: id}, (resp) => {
                    console.log("subscription result:");
                    console.log(resp.obj);
                    if(resp.obj.success==true){
                        setTimeout(() => this.actions.reportProgress(rep.obj.progress, resp.obj.total))
                        resolve()
                    }else if(resp.obj.success==false){
                        reject(resp);
                    }else{
                        setTimeout(() => {
                            this.actions.reportProgress(resp.obj.progress, resp.obj.total);
                            this.actions.checkSubscriptionResult(id).then(resolve, reject);
                        })
                    }
                })
            });
        })
    }

    reportProgress(progress, total){
        return {
            total: total,
            progress: progress
        };
    }

    unsubscribe(podcastIds){
        if(podcastIds.constructor !== Array){
            podcastIds = [podcastIds];
        }

        heap.track("subscribe", {podcastIds: podcastIds.join(",")})
        return new Promise((resolve, reject) => {
            api.loaded.then(() => {
                api.users.unsubscribe({userId: "me", podcast: podcastIds}, (resp) => {
                    if (resp.obj.success){
                        this.dispatch(podcastIds);
                        resolve()
                        this.actions.fetchSubscriptions("me");
                    }else{
                        reject(resp);
                    }
                });
            });
        });
    }

    fetchPodcast(podcastId){
        return new Promise((resolve, reject) => {
            api.loaded.then(() => {
                api.podcasts.getPodcast({podcastId: podcastId, fetch: true}, (resp) => {
                    if(resp.status !== 200){
                        reject(resp.statusText);
                        return
                    }
                    this.dispatch(transformPodcast(resp.obj));
                });
            });
        });
    }

    fetchEpisodes(podcastId, page, perPage=30){
        return new Promise((resolve, reject) => {
            api.loaded.then(() => {
                api.podcasts.getEpisodes({podcastId: podcastId, perPage: perPage, page: page}, (resp) => {
                    if(resp.status !== 200){
                        reject(resp.statusText);
                        return
                    }
                    resolve();
                    this.dispatch({result: resp.obj, podcastId: podcastId});
                });
            });
        });
    }

    fetchSubscriptions(userId){
        userId = userId || "me"
        setTimeout(() => this.actions.fetchingSubscriptions(userId));
        return new Promise((resolve, reject) => {
            api.loaded.then(() => {
                api.users.getSubscriptions({userId: userId}, (resp) => {
                    if(resp.status !== 200){
                        reject(resp.statusText);
                        return
                    }
                    this.dispatch({
                        userSubscriptions: resp.obj.map(transformPodcast),
                        userId: userId
                    })
                })
            });
        });
    }

    fetchingSubscriptions(userId){
        return userId
    }

    fetchPopularPodcasts(){
        return new Promise((resolve, reject) => {
            api.loaded.then(() => {
                api.podcasts.query({order:"subscribers"}, (res) => {
                    this.dispatch(res.obj.map(transformPodcast));
                });
            });
        });
    }
});

module.exports = PodcastActions;
