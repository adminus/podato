const React = require("react");
const Link = require("react-router").Link;


const PlayBar = React.createClass({
    render(){
        return (
            <nav className="fixed bottom-0 left-0 right-0 bg-red white px4" style={{height:"2.5rem"}}>
                <div className="container flex flex-stretch">
                    <button className="button button-red"><i className="el el-backward" /></button>
                    <button className="button button-red"><i className="el el-play" /></button>
                    <button className="button button-red"><i className="el el-forward" /></button>
                </div>
            </nav>
        )
    }
});

module.exports = PlayBar;
