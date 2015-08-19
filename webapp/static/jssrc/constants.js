const km = require('keymirror')

module.exports = {
    actionTypes: km({
        LOGGED_IN:null,
        LOGGED_OUT:null,
        LOGGING_IN:null,
        LOGGING_OUT: null,
        LOGIN_CANCELLED: null,
        PODCAST_FETCHED:null,
        POPULAR_PODCASTS_FETCHED: null,
        SUBSCRIPTIONS_FETCHED: null,
        FETCHING_SUBSCRIPTIONS: null,
        SUBSCRIBED: null,
        UNSUBSCRIBED: null,
        USER_FETCHED: null,
        FOLLOWED: null,
        UNFOLLOWED: null,
        SUBSCRIBE_PROGRESS: null,
    })
}
