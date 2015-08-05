const mcfly = require("../mcfly");
const constants = require("../constants");

var loggingIn = false;

const CurrentUserStore = mcfly.createStore({
    getLoggingIn(){return loggingIn},
    getCurrentUser(){return JSON.parse(localStorage.currentUser)}
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
            currentUser.following.concat(data.userIds);
            localStorage.currentUser = JSON.stringify(currentUser);
            break;
        case constants.actionTypes.UNFOLLOWED:
            var currentUser = CurrentUserStore.getCurrentUser();
            for(var i=0; i<data.userIds.length; i++){
                var id = data.userIds[i];
                var index = currentUser.following.indexOf(id);
                if(index >= 0){
                    currentUser.following.splice(index, 1)
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
