const React = require("react");
const ListenerMixin = require("alt/mixins/ListenerMixin");

const PlaybackActions = require("../../actions/playback-actions");

const utils = require("../../utils")

const ProgressBar = React.createClass({
    render(){
        const height = this.state.pointerX ? "0.8em" : "0.3em";
        const styles = {
            position: "absolute",
            left: 0,
            right: 0,
            top: "-" + height,
            height: height,
            background : "rgb(241, 221, 0)",
            transition: "height 0.3s, top 0.3s"
        };
        const barStyles = {
            width: (this.props.progress * 100) + "%",
            height: "100%",
            background: "rgba(0, 0, 0, 0.7)",
            content: "\t"
        };
        const pointerStyles = {
            background: "black",
            position:"absolute",
            left: this.state.pointerX,
            top: "-32",
            transform: "translate(-50%, 0)",
            display: this.state.pointerX ? "block": "none"
        }
        const pointerTriangle = {
            width: "0",
            eight: "0",
            borderStyle: "solid",
            borderWidth: "16px 8px 0 9px",
            borderColor: "#000 transparent transparent transparent",
            position: "absolute",
            top: "100%",
            left: "50%",
            transform: "translate(-50%, 0)"
        };
        return (
            <div ref="element" style={styles} onMouseMove={this.mouseMove} onMouseLeave={this.mouseLeave} onClick={this.click}>
                <div style={pointerStyles}><div style={pointerTriangle}>&nbsp;</div>{utils.formatTime(this.props.duration*this.state.pointerProgress)}</div>
                <div className="bg-red" style={barStyles}></div>
            </div>
        )
    },
    mouseMove(e){
        const ow = this.refs.element.getDOMNode().offsetWidth;
        this.setState({
            pointerX: e.clientX,
            pointerProgress: e.clientX/ow
        });
    },
    mouseLeave(){
        this.setState({pointerX: null});
    },
    click(e){
        PlaybackActions.seek(this.state.pointerProgress * this.props.duration);
    },
    getInitialState(){
        console.log("duration: "+this.props.duration);
        return {
            pointerX: null,
            pointerProgress: null,
        };
    }
});

module.exports = ProgressBar;
