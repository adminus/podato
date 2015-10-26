const api = require("./api.js");
var config = require("config");

var apiRoot = void(0)
if(location.hostname === "localhost"){
    apiRoot = location.origin;
}
api.load(apiRoot, config.get("TRUSTED_CLIENTS[0].CLIENT_ID")[0], Object.keys(config.get("OAUTH_SCOPES")[0]).join(" "));


const docReady = require("doc-ready");

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

api.loaded.then(() =>{
    console.log("api loaded");
    console.log(api);
})

const routes = (
    <Router>
        <Route path="/" component={App}>
            <IndexRoute component={Home} />
            <Route path="podcasts/*" component={Podcast} />
            <Route path="users/:userId" component={User} />
        </Route>
    </Router>
);

window.ReactRouter = ReactRouter;

docReady(() => {
    ReactDOM.render(routes, document.getElementById("app"));
});
