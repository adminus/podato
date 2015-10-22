const flux = require("../flux");
const SearchActions = require("../actions/search-actions");


const UsersStore = flux.createStore(class UsersStore{
    constructor(){
        this.results = [];
        this.bindActions(SearchActions);
    }

    static getResults(){
        return this.state.results;
    }

    onSearch(results){
        this.results = results;
    }
}, "SearchStore");

module.exports = UsersStore;
