const mcfly = require("../mcfly");
const constants = require("../constants");

var loggingIn = false;

const CurrentUserStore = mcfly.createStore({
    getLoggingIn(){return loggingIn},
    getCurrentUser(){return JSON.parse(localStorage.currentUser)},
    isFollowing(otherId){
        var user = CurrentUserStore.getCurrentUser();
        for(var i=0; i<user.following.length; i++){
            if(user.following[i].id == otherId){
                return true;
            }
        }
        return false;
    }
}, function(data){
    switch(data.actionType){
        case constants.actionTypes.LOGGING_IN:
            loggingIn = true;
            break;
        case constants.actionTypes.LOGGED_IN:
            loggingIn = false;
            localStorage.currentUser = JSON.stringify(data.user);
            break;
        case constants.actionTypes.LOGGED_OUT:
            loggingIn = false;
            localStorage.currentUser = null;
            break;
        case constants.actionTypes.LOGIN_CANCELLED:
            loggingIn = false;
            break;
        case constants.actionTypes.FOLLOWED:
            var currentUser = CurrentUserStore.getCurrentUser();
            var idObjects = [];
            for(var i=0; i<data.userIds.length; i++){
                idObjects.push({id: data.userIds[i]})
            }
            Array.prototype.push.apply(currentUser.following, idObjects);
            localStorage.currentUser = JSON.stringify(currentUser);
            break;
        case constants.actionTypes.UNFOLLOWED:
            var currentUser = CurrentUserStore.getCurrentUser();
            for(var i=0; i<data.userIds.length; i++){
                for(var j=0; j<currentUser.following.length; j++){
                    if(currentUser.following[j].id == data.userIds[i]){
                        currentUser.following.splice(j, 1)
                    }
                }
            }
            localStorage.currentUser = JSON.stringify(currentUser);
            break;
        default:
            return
    }
    CurrentUserStore.emitChange();
});

module.exports = CurrentUserStore;
