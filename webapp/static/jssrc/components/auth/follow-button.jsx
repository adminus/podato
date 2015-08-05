const React = require("react");

const UserActions = require("../../actions/user-actions.js");

const CurrentUserStore = require("../../stores/current-user-store");
const Spinner = require("../common/spinner.jsx");

const FollowButton = React.createClass({
    mixins: [CurrentUserStore.mixin],
    render(){
        if(!this.state.user) return (<span>Log in to subscribe.</span>);

        var className = "button " + (this.props.className || "");
        if(!this.state.isFollowing){
            return (
                <button {...this.props} className={className} onClick={this.follow} disabled={this.state.disabled}>Follow</button>
            )
        }
        className = "button bg-darken-4" + (this.props.className || "");
        return (
            <button {...this.props} className={className} onClick={this.unfollow} disabled={this.state.disabled}>Unfollow</button>
        )

    },
    makeState(){
        var user = CurrentUserStore.getCurrentUser();
        return {
            user: user,
            isFollowing: user.following.indexOf(this.props.user.id) >= 0
        }
    },
    getInitialState(){
        return this.makeState();
    },
    follow(e){
        e.preventDefault();
        UserActions.follow(this.props.user);
        this.setState({disabled: true})
    },
    unfollow(e){
        e.preventDefault();
        UserActions.unfollow([this.props.user]);
        this.setState({disabled: true})
    },
    storeDidChange(){
        var newState = this.makeState();
        if(newState.isFollowing !== this.state.isFollowing){
            newState.disabled=false;
        }
        this.setState(newState);
    }
});

module.exports = FollowButton;
