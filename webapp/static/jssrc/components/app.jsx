const React = require("react");
const Navbar = require("./navbar/navbar.jsx");
const Playbar = require("./playbar/playbar.jsx");

const App = React.createClass({
    render() {
        return (
            <div className="clearfix">
                <Navbar />
                <div className="container mt4">
                    {this.props.children}
                </div>
                <Playbar />
            </div>
        );
    }
});

module.exports = App
