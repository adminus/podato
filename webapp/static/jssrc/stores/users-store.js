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

    static getUser(id){
        return this.state.users[id]
    }

    onFetchUser(user){
        this.users[user.id] = user
    }
}, "UsersStore");

module.exports = UsersStore;
