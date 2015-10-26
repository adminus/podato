const React = require("react");
const History = require("react-router").History;
const ListenerMixin = require("alt/mixins/ListenerMixin");

const UsersStore = require("../../stores/users-store");
const AuthActions = require("../../actions/auth-actions");
const CurrentUserStore = require("../../stores/current-user-store");

const Image = require("../common/image.jsx");
const Page = require("../common/page.jsx");
const SubscriptionsGrid = require("../podcasts/subscriptions-grid.jsx")
const FollowButton = require("../auth/follow-button.jsx")

const User = React.createClass({
    mixins: [History, ListenerMixin],
    render(){
        return (
            <Page>
                <div className="clearfix mxn2">
                    <div className="sm-col-12 p2">
                        <h1>{this.state.user.username}</h1>
                    </div>
                </div>
                <div className="clearfix mxn2">
                    <div className="sm-col sm-col-1 md-col-3 p2">
                        <Image src={this.state.user.avatar_url} className="full-width" />
                        <p><FollowButton user={this.state.user}/></p>
                    </div>
                    <div className="sm-col sm-col-11 md-col md-col-9 p2">
                        <h2>Subscriptions</h2>
                        <div className="clearfix mxn1">
                            {this.state.user.id ? (<SubscriptionsGrid userId={this.state.user.id} />) : "..."}
                        </div>
                    </div>
                </div>
            </Page>
        );
    },
    getInitialState(){
        return {user:{
            username: "Loading ...",
            avatar_url: "https://podato.herokuapp.com/img/logo.png"
        }};
    },
    componentWillMount(){
        this.setUser();
        this.listenTo(CurrentUserStore, this.storeDidChange);
        this.listenTo(UsersStore, this.storeDidChange);
    },
    componentWillReceiveProps(){
        this.setUser();
    },
    storeDidChange(){
        this.setUser();
    },
    setUser(){
        const userId = this.props.params.userId;
        if(userId == "me"){
            const me = CurrentUserStore.getState().currentUser.id;
            this.history.pushState(null, `/users/${me}`);
        }
        var user = UsersStore.getUser(userId);

        if (!user){
            AuthActions.fetchUser(userId);
        }else{
            this.setState({user:user});
        }
    }
});

module.exports = User;
