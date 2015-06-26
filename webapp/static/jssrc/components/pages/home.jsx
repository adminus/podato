const React = require("react");

const LoginButton = require("../auth/login-button.jsx")
const PodcastGrid = require("../podcasts/podcast-grid.jsx")
const CurrentUserStore = require("../../stores/current-user-store");
const PopularPodcastsStore = require("../../stores/popular-podcasts-store");
const SubscriptionsStore = require("../../stores/subscriptions-store");
const PodcastActions = require("../../actions/podcast-actions");

const Home = React.createClass({
    mixins: [CurrentUserStore.mixin, PopularPodcastsStore.mixin, SubscriptionsStore.mixin],
    render(){
        var auth = [
            (<LoginButton authProvider="Facebook" className="m1" key="a1" />),
            (<LoginButton authProvider="Twitter" className="m1" key="a2" />),
            (<LoginButton authProvider="Google" className="m1" key="a3" />)
        ];
        if(this.state.authState === "progress") {
            auth = (<img src="/img/loading_bar.gif" />)
        }
        if(this.state.authState === "done") {
            auth = (<a>Get started</a>);
            var subscriptions = [
                <h3 key="heading">Subscriptions</h3>,
                <PodcastGrid podcasts={this.state.userSubscriptions} className="sm-col sm-col-12" key="grid" />,
                <hr key="hr" />
                ]
        }

        return (
            <div className="bg-white rounded p2 px4">
                <h1 className="center">Podato</h1>
                <h2 className="center">Enjoy Podcasts Together</h2>
                <p className="center">
                    {auth}
                </p>
                <div className="clearfix">
                    {subscriptions}
                </div>
                <h3>Popular podcasts</h3>
                <div className="clearfix">
                    <PodcastGrid podcasts={this.state.popularPodcasts} className="sm-col sm-col-12" />
                </div>
                <hr />
            </div>
        );
    },
    componentWillMount() {
        PodcastActions.fetchPopularPodcasts();
    },
    componentWillReceiveProps() {
        if(CurrentUserStore.getCurrentUser != null){
            PodcastActions.fetchSubscriptions("me");
        }
    },
    getInitialState(){
        return {authState: null, popularPodcasts: [], userSubscriptions: []};
    },
    storeDidChange(){
        var authState = null;
        if(CurrentUserStore.getCurrentUser() == null){
            if (CurrentUserStore.getLoggingIn()) {
                authState = "progress";
            }
        }else{
            authState = "done";
        }
        if (this.state.authState != "done" && authState == "done"){ //If the user has just logged in,
            PodcastActions.fetchSubscriptions("me");                //Fetch the user's subscriptions
        }
        this.setState({
            authState: authState,
            popularPodcasts: PopularPodcastsStore.get(),
            userSubscriptions: SubscriptionsStore.getSubscriptions("me") || [   ]
        });
    }
});

module.exports = Home
