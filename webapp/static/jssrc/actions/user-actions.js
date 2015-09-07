const flux = require("../flux");
const api = require("../api");


const UserActions = flux.createActions(class UserActions {
    follow(userIds){
        if(userIds.constructor !== Array){
            userIds = [userIds];
        }
        heap.track("follow", {userIds: userIds.join(",")})
        return new Promise((resolve, reject) => {
            api.loaded.then(() => {
                api.users.follow({userId: "me", otherUser:userIds}, (resp) => {
                    this.dispatch(userIds);
                });
            });
        });
    }

    unfollow(userIds){
        if(userIds.constructor !== Array){
            userIds = [userIds];
        }
        heap.track("unfollow", {userIds: userIds.join(",")})
        return new Promise((resolve, reject) => {
            api.loaded.then(() => {
                api.users.unfollow({userId: "me", otherUser: userIds}, (resp) => {
                    this.dispatch(userIds);
                });
            });
        });
    }
});

module.exports = UserActions;
