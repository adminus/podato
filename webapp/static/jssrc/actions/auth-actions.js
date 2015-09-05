const flux = require("../flux");
const api = require("../api");

const AuthActions = flux.createActions(class AuthActions {
    constructor(){
        this.generateActions("loggingIn", "loggedIn", "loggedOut", "loginCancelled");
    }

    login(authProvider){
        api.login(authProvider);
        this.actions.loggingIn();
    }

    logout(){
        heap.track("logout", {})
        API.users.logout({}, (res) => {
            if(res.obj.success){
                api.logout();
            }
        })
        return {}
    }

    fetchUser(userId){
        api.loaded.then(() => {
            api.users.getUser({userId: userId}, (resp) => {
                this.dispatch(resp.obj);
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
