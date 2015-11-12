const React = require("react");
const GraphiQL = require("graphiql");
const api = require("../../api");

const fetcher = (payload) => {
    console.log("sending graphql query:")
    console.log(payload);
    return new Promise((resolve, reject) => {
        api.loaded.then(() => {
            api.graphql.query({query: payload.query}, (response) => {
                if(!response.obj.data){
                    reject(response.obj);
                    return;
                }
                resolve(response.obj);
            });
        });
    });
}

module.exports = () => {
    return <GraphiQL fetcher={fetcher}/>
}
