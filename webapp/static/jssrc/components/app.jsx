const React = require("react");
const RouteHandler = require("react-router").RouteHandler;
const Navbar = require("./navbar/navbar.jsx");
const Playbar = require("./playbar/playbar.jsx");

const App = React.createClass({
    render() {
        return (
            <div className="clearfix">
                <Navbar />
                <div className="container mt4">
                    <RouteHandler />
                </div>
                <Playbar />
            </div>
        );
    }
});

module.exports = App
