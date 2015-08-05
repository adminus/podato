const mcfly = require("../mcfly");
const api = require("../api");
const constants = require("../constants");


const UserActions = mcfly.createActions({
    follow(userIds){
        if(userIds.constructor !== Array){
            userIds = [userIds];
        }
        heap.track("follow", {userIds: userIds.join(",")})
        return new Promise((resolve, reject) => {
            api.loaded.then(() => {
                api.users.follow({userId: "me", otherUser:userIds}, (resp) => {
                    resolve({
                        actionType: constants.actionTypes.FOLLOWED,
                        userIds: userIds
                    });
                });
            });
        });
    },
    unfollow(userIds){
        if(userIds.constructor !== Array){
            userIds = [userIds];
        }
        heap.track("unfollow", {userIds: userIds.join(",")})
        return new Promise((resolve, reject) => {
            api.loaded.then(() => {
                api.users.unfollow({userId: "me", otherUser: userIds}, (resp) => {
                    resolve({
                        actionType: constants.actionTypes.UNFOLLOWED,
                        userIds: userIds
                    });
                });
            });
        });
    }
});

module.exports = UserActions;
