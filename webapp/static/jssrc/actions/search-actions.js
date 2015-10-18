const flux = require("../flux");
const api = require("../api");
const utils = require("../utils")

const SearchActions = flux.createActions(class UserActions {
    search(query){
        return new Promise((resolve, reject) => {
            utils.fetchJSONP("https://itunes.apple.com/search", {
                term: query,
                media: "podcast"
            }).then((result) => {
                console.log("search result:");
                console.log(result);
                this.dispatch(result.results);
                resolve();
            })
        });
    }
});

module.exports = SearchActions;
