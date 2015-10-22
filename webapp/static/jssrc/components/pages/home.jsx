const React = require("react");
const ListenerMixin = require("alt/mixins/ListenerMixin");

const LoginButton = require("../auth/login-button.jsx");
const PodcastGrid = require("../podcasts/podcast-grid.jsx");
const ImportButton = require("../podcasts/import-button.jsx");
const Page = require("../common/page.jsx");

const CurrentUserStore = require("../../stores/current-user-store");
const PopularPodcastsStore = require("../../stores/popular-podcasts-store");
const SubscriptionsStore = require("../../stores/subscriptions-store");
const PodcastActions = require("../../actions/podcast-actions");


const Home = React.createClass({
    mixins: [ListenerMixin],
    render(){
        var auth = this.getAuthButtons();
        var subscriptions = this.getSubscriptionsGrid();

        return (
            <Page>
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
            </Page>
        );
    },
    getAuthButtons(){
        var auth = [
            (<LoginButton authProvider="Facebook" className="m1" key="auth-1" />),
            (<LoginButton authProvider="Twitter" className="m1" key="auth-2" />),
            (<LoginButton authProvider="Google" className="m1" key="auth-3" />)
        ];

        if(this.state.authState === "progress") {
            auth = (<img src="/img/loading_bar.gif" />)
        }
        if(this.state.authState === "done") {
            auth = (<a>Get started</a>);
        }
        return auth
    },
    getSubscriptionsGrid(){
        if(this.state.authState === "done") {
            return [
                <h3 key="heading">Subscriptions</h3>,
                <ImportButton key="import" />,
                <PodcastGrid podcasts={this.state.userSubscriptions} className="sm-col sm-col-12" key="grid" />,
                <hr key="hr" />
            ]
        }
    },
    componentWillMount() {
        PodcastActions.fetchPopularPodcasts();
        this.listenTo(CurrentUserStore, this.storeDidChange);
        this.listenTo(PopularPodcastsStore, this.storeDidChange);
        this.listenTo(SubscriptionsStore, this.storeDidChange);
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
        if(CurrentUserStore.getState().currentUser == null){
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
