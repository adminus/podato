const mcfly = require("../mcfly");
const constants = require("../constants");
const utils = require("../utils.js");
//When we need to show an overview of the user's subscriptions, we fetch the full list, and store it here.
var subscriptions = {};
//When a user subscribes to a podcast, we only store the podcast's url here.
var subscribed_urls = [];
//a list of user ID's whose subscriptions are currently being fetched.
var fetching = []
//progress of a subscription request
var progress = null;

const SubscriptionsStore = mcfly.createStore({
    getSubscriptions(userId){return subscriptions[userId]},
    isFetchingSubscriptions(userId){return (fetching.indexOf(userId) >= 0)},
    getProgress(){return progress},

    isSubscribedTo(userId, podcast){
        var in_subscriptions = (subscriptions[userId] && subscriptions[userId].filter((p) => {
            return p.id == podcast;
        }).length > 0);
        var in_subscribed_urls = (userId === "me" && subscribed_urls.indexOf(podcast) >= 0);
        return (in_subscriptions || in_subscribed_urls);
    }
}, function(data){
    switch(data.actionType){
        case constants.actionTypes.SUBSCRIPTIONS_FETCHED:
            subscriptions[data.userId] = data.userSubscriptions;
            if (fetching.indexOf(data.userId) >= 0){
                fetching.splice(fetching.indexOf(data.userId), 1);
            }
            break;
        case constants.actionTypes.FETCHING_SUBSCRIPTIONS:
            fetching.push(data.userId);
            break;
        case constants.actionTypes.SUBSCRIBED:
            subscribed_urls = utils.unique(subscribed_urls.concat(data.podcasts));
            break;
        case constants.actionTypes.UNSUBSCRIBED:
            subscriptions.me = subscriptions.me.filter((item) => {
                return data.podcasts.indexOf(item.id) < 0;
            });
            subscribed_urls = subscribed_urls.filter((item) => {
                return data.podcasts.indexOf(item) < 0;
            });
            break;
        case constants.actionTypes.SUBSCRIBE_PROGRESS:
            progress = data.progress / data.total;
            if(progress === 1){
                progress = null;
            }
            break;
        default:
            return
    }
    SubscriptionsStore.emitChange();
});

module.exports = SubscriptionsStore;
