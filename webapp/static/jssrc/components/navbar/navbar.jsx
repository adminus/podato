const React = require("react");
const Link = require("react-router").Link;
const ListenerMixin = require("alt/mixins/ListenerMixin");

const SearchBox = require("./search-box.jsx");

const CurrentUserStore = require("../../stores/current-user-store");
const AuthActions = require("../../actions/auth-actions");


const Navbar = React.createClass({
    mixins: [ListenerMixin],
    componentWillMount(){
        this.listenTo(CurrentUserStore, this.storeDidChange);
    },
    render(){
        var logout = ""
        if(this.state.user){
            logout = <a className="col col-1" onClick={AuthActions.logout} className="button button-red">Log out</a>
        }
        return (
            <nav className="fixed top-0 left-0 right-0 bg-red white" style={{height:"2.5rem"}}>
                <div className="container">
                    <div className="clearfix" style={{height:"2.5rem"}}>
                        <Link to="/" className="col col-1" style={{height:"100%"}}><img src="/img/logo.png" style={{height:"100%"}}/></Link>
                        <Link to="/" className="button button-red col col-1">Home</Link>
                        <SearchBox className="col col-4" />
                        {logout}
                    </div>
                </div>
            </nav>
        )
    },
    getInitialState(){
        return {user: CurrentUserStore.getState().currentUser}
    },
    storeDidChange(){
        this.setState({user: CurrentUserStore.getState().currentUser})
    }
});

module.exports = Navbar;
