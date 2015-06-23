const React = require("react");
const PodcastGrid = require("./podcast-grid.jsx");
const SubscriptionsStore = require("../../stores/subscriptions-store")
const PodcastsActions = require("../../actions/podcast-actions");

const SubscriptionsGrid = React.createClass({
    mixins:[SubscriptionsStore.mixin],
    render(){
        return <PodcastGrid {...this.props} podcasts={this.state.subscriptions}/>
    },
    makeState(){
        const subs = SubscriptionsStore.getSubscriptions(this.props.userId);
        if(subs === undefined && !SubscriptionsStore.isFetchingSubscriptions(this.props.userId)){
            PodcastsActions.fetchSubscriptions(this.props.userId);
        }
        return {subscriptions: subs}
    },
    getInitialState(){
        return this.makeState();
    },
    storeDidChange(){
        this.setState(this.makeState());
    }
});

module.exports = SubscriptionsGrid;
