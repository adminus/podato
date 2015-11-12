const api = require("./api.js");
var config = require("config");

var apiRoot = void(0)
if(location.hostname === "localhost"){
    apiRoot = location.origin;
}
api.load(apiRoot, config.get("TRUSTED_CLIENTS[0].CLIENT_ID")[0], Object.keys(config.get("OAUTH_SCOPES")[0]).join(" "));


const docReady = require("doc-ready");
const createHistory = require("history").createHistory

const React = require("react");
const ReactDOM = require('react-dom');
const ReactRouter = require("react-router");
const Route = ReactRouter.Route;
const IndexRoute = ReactRouter.IndexRoute;
const Router = ReactRouter.Router;

const App = require("./components/app.jsx");
const Home = require("./components/pages/home.jsx");
const Podcast = require("./components/pages/podcast.jsx");
const User = require("./components/pages/user.jsx");
const GraphQL = require("./components/pages/graphql.jsx");

// Opt-out of persistent state,
let history = createHistory({
  queryKey: false
});

api.loaded.then(() =>{
    console.log("api loaded");
    console.log(api);
})

const routes = (
    <Router history={createHistory()}>
        <Route path="/" component={App}>
            <IndexRoute component={Home} />
            <Route path="podcasts/*" component={Podcast} />
            <Route path="users/:userId" component={User} />
        </Route>
        <Route path="/graphql" component={GraphQL}/>
    </Router>
);

window.ReactRouter = ReactRouter;

docReady(() => {
    ReactDOM.render(routes, document.body);
});
