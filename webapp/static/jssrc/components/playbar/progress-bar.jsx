const React = require("react");
const ListenerMixin = require("alt/mixins/ListenerMixin");

const PlaybackStore = require("../../stores/playback-store");

const ProgressBar = React.createClass({
    render(){
        const height = "0.5em";
        const styles = {
            position: "absolute",
            left: 0,
            right: 0,
            top: "-" + height,
            height: height,
            background : "rgb(241, 221, 0)",
        };
        const barStyles = {
            width: (this.props.progress * 100) + "%",
            height: "100%",
            background: "rgba(0, 0, 0, 0.7)",
            content: "\t"
        };
        return (
            <div style={styles}>
                <div className="bg-red" style={barStyles}></div>
            </div>
        )
    }
});

module.exports = ProgressBar;
