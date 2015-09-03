const flux = require("../flux");
const utils = require("../utils.js");
const PodcastActions = require("../actions/podcast-actions");

const SubscriptionsStore = flux.createStore(class SubscriptionsStore{
    constructor(){
        //When we need to show an overview of the user's subscriptions, we fetch the full list, and store it here.
        this.subscriptions = {};
        //When a user subscribes to a podcast, we only store the podcast's url here.
        this.subscribedUrls = [];
        //a list of user ID's whose subscriptions are currently being fetched.
        this.fetching = []
        //progress of a subscription request
        this.progress = null;

        this.bindActions(PodcastActions);
    }

    getSubscriptions(userId){
        return this.subscriptions[userId]
    }

    isFetchingSubscriptions(userId){
        return (this.fetching.indexOf(userId) >= 0)
    }

    getProgress(){
        return this.progress;
    },

    isSubscribedTo(userId, podcast){
        var in_subscriptions = (this.subscriptions[userId] && this.subscriptions[userId].filter((p) => {
            return p.id == podcast;
        }).length > 0);

        var in_subscribed_urls = (userId === "me" && this.subscribedUrls.indexOf(podcast) >= 0);

        return (in_subscriptions || in_subscribed_urls);
    }

    onFetchSubscriptions(data){
        this.subscriptions[data.userId] = data.userSubscriptions;
        if (this.fetching.indexOf(data.userId) >= 0){
            this.fetching.splice(this.fetching.indexOf(data.userId), 1);
        }
    }

    onFetchingSubscriptions(userId){
        this.fetching.push(userId);
    }

    onSubscribe(podcastIds){
        this.subscribedUrls = utils.unique(this.subscribedUrls.concat(podcastIds))
    }

    onUnsubscribe(podcastIds){
        this.subscriptions.me = this.subscriptions.me.filter((item) => {
            return data.podcasts.indexOf(item.id) < 0;
        });
        this.subscribedUrls = this.subscribedUrls.filter((item) => {
            return data.podcasts.indexOf(item) < 0;
        });
    }

    onReportProgress(progressObj){
        this.progress = progressObj.progress / progressObj.total;
        if(this.progress == 1){
            this.progress = null;
        }
    }
});

module.exports = SubscriptionsStore;
