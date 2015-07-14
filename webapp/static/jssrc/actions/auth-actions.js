const mcfly = require("../mcfly");
const api = require("../api");
const constants = require("../constants");

const AuthActions = mcfly.createActions({
    login(authProvider){
        return new Promise((resolve, reject) => {
            api.login(authProvider);
            AuthActions.loggingIn();
        });
    },
    loggingIn(){
        return {actionType: constants.actionTypes.LOGGING_IN}
    },
    loggedIn(user){
        return {
            actionType: constants.actionTypes.LOGGED_IN,
            user: user
        };
    },
    logout(){
        heap.track("logout", {})
        API.users.logout({}, (res) => {
            if(res.obj.success){
                api.logout();
            }
        })
        return {
            actionType: constants.actionTypes.LOGGING_OUT
        }
    },
    loggedOut(){
        return {
            actionType: constants.actionTypes.LOGGED_OUT
        }
    },
    loginCancelled(){
        return {
            actionType: constants.actionTypes.LOGIN_CANCELLED
        }
    },
    fetchUser(userId){
        return new Promise((resolve, reject) => {
            api.loaded.then(() => {
                api.users.getUser({userId: userId}, (resp) => {
                    resolve({
                        actionType: constants.actionTypes.USER_FETCHED,
                        user: resp.obj
                    });
                });
            });
        });
    }
});

var authListener = () => {
    AuthActions.loggingIn();
    api.loaded.then(() => {
        api.users.getUser({userId: "me"}, (resp) => {
            AuthActions.loggedIn(resp.obj)
            heap.identify({handle: resp.obj.username, podato_id:resp.obj.id});
        });
    });
};

var unauthListener = () => {
    AuthActions.loggedOut();
}

var cancelListener = () => {
    AuthActions.loginCancelled();
}

api.addListener("unauthenticated", unauthListener);
api.addListener("loginCancelled", cancelListener)
api.addListener("authenticated", authListener);

if(api.isLoggedIn()){
    authListener();
}else{
    unauthListener();
}

module.exports = AuthActions;
