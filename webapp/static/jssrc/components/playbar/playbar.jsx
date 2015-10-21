const React = require("react");
const Link = require("react-router").Link;
const ListenerMixin = require("alt/mixins/ListenerMixin");
const utils = require("../../utils");
const Image = require("../common/image.jsx");

const PlaybackStore = require("../../stores/playback-store");
const PlaybackActions = require("../../actions/playback-actions");

const ProgressBar = require("./progress-bar.jsx");

const PlayBar = React.createClass({
    mixins: [ListenerMixin],
    render(){
        if(!this.state.episode){
            return null;
        }
        var playButton = <button className="button button-red col col-1" onClick={this.play} style={{height:"2.5rem"}}><i className="el el-play" /></button>
        if(this.state.playing){
            playButton = <button className="button button-red col col-1" onClick={this.pause} style={{height:"2.5rem"}}><i className="el el-pause"/></button>
        }
        return (
            <nav className="fixed bottom-0 left-0 right-0 bg-red white px4" style={{height:"2.5rem"}}>
                <ProgressBar progress={this.state.progress} duration={this.state.duration}/>
                <div className="container">
                    <div className="clearfix" style={{height:"2.5rem"}}>
                        <div className="col col-1"><Image src={this.state.episode.image} style={{height: "2.5rem"}} /></div>
                        <button className="button button-red col col-1" style={{height:"2.5rem"}}><i className="el el-backward" /></button>
                        {playButton}
                        <button className="button button-red col col-1" style={{height:"2.5rem"}}><i className="el el-forward" /></button>
                        <div className="col col-3" style={{height:"2.5rem", "lineHeight":"2.5rem"}}>{utils.formatTime(this.state.currentTime)} / {utils.formatTime(this.state.duration)}</div>
                    </div>
                </div>
            </nav>
        )
    },
    getInitialState(){
        return this.makeState()
    },
    componentWillMount(){
        this.listenTo(PlaybackStore, this.storeDidChange);
    },
    storeDidChange(){
        this.setState(this.makeState());
    },
    makeState(){
        return {
            playing: PlaybackStore.getState().playing,
            episode: PlaybackStore.getState().currentEpisode,
            duration: PlaybackStore.getState().duration,
            currentTime: PlaybackStore.getState().currentTime,
            progress: PlaybackStore.getState().currentTime / PlaybackStore.getState().duration
        }
    },
    play(){
        PlaybackActions.resume();
    },
    pause(){
        PlaybackActions.pause();
    }
});

module.exports = PlayBar;
