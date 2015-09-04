const flux = require("../flux");
const UserActions = require("../actions/user-actions");
const AuthActions = require("../actions/auth-actions");

var users = {}

const UsersStore = flux.createStore(class UsersStore{
    constructor(){
        this.users = {};
        this.bindActions(UserActions);
        this.bindActions(AuthActions);
    }

    getUser(id){
        return users[id]
    }

    onFetchUser(user){
        users[user.id] = user
    }
}, "UsersStore");

module.exports = UsersStore;
