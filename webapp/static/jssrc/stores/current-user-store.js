const flux = require("../flux");
const AuthActions = require("../actions/auth-actions");
const UserActions = require("../actions/user-actions");

const CurrentUserStore = flux.createStore(class {
    constructor(){
        this.loggingIn = false;
        //JSON.parse doesn't deal well with undefined, so we pass in null instead
        this.currentUser = JSON.parse(localStorage.currentUser || null);
        this.bindActions(AuthActions);
        this.bindActions(UserActions);
    }

    static isFollowing(otherId){
        for(var i=0; i<this.state.currentUser.following.length; i++){
            if(this.state.currentUser.following[i].id == otherId){
                return true;
            }
        }
        return false;
    }

    static getLoggedIn(){
        return this.state.currentUser != null;
    }

    static getLoggingIn(){
        return this.state.loggingIn;
    }

    onLoggingIn(){
        this.loggingIn = true
    }

    onLoggedIn(user){
        this.loggingIn = false;
        this.currentUser = user;
        localStorage.currentUser = JSON.stringify(user);
    }

    onLoggedOut(){
        this.currentUser = null;
        localStorage.currentUser = null;
        this.loggingIn = false;
    }

    onLoginCancelled(){
        this.loggingIn = false;
    }

    onFollow(userIds){
        var idObjects = [];
        for(var i=0; i<userIds.length; i++){
            idObjects.push({id: userIds[i]});
        }
        this.currentUser.following.push(...idObjects);
        localStorage.currentUser = JSON.stringify(this.currentUser);
    }

    onUnfollow(userIds){
        for(var i=0; i< userIds.length; i++){
            for(var j=0; j<this.currentUser.following.length; j++){
                if(this.currentUser.following[j].id == userIds[i]){
                    this.currentUser.following.splice(j, 1)
                }
            }
        }
        localStorage.currentUser = JSON.stringify(this.currentUser);
    }
}, "CurrentUserStore");

module.exports = CurrentUserStore;
