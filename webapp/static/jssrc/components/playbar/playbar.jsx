const React = require("react");
const Link = require("react-router").Link;
const ListenerMixin = require("alt/mixins/ListenerMixin");

const Image = require("../common/image.jsx");

const PlaybackStore = require("../../stores/playback-store");
const PlaybackActions = require("../../actions/playback-actions");

const PlayBar = React.createClass({
    mixins: [ListenerMixin],
    render(){
        if(!this.state.episode){
            return null;
        }
        var playButton = <button className="button button-red" onClick={this.play}><i className="el el-play" /></button>
        if(this.state.playing){
            playButton = <button className="button button-red" onClick={this.pause}><i className="el el-pause"/></button>
        }
        return (
            <nav className="fixed bottom-0 left-0 right-0 bg-red white px4" style={{height:"2.5rem"}}>
                <div className="container flex flex-stretch">
                    <Image src={this.state.episode.image} style={{height: "2.5rem"}} />
                    <button className="button button-red"><i className="el el-backward" /></button>
                    {playButton}
                    <button className="button button-red"><i className="el el-forward" /></button>
                </div>
            </nav>
        )
    },
    getInitialState(){
        return {
            playing: PlaybackStore.getState().playing,
            episode: PlaybackStore.getState().currentEpisode
        }
    },
    componentWillMount(){
        this.listenTo(PlaybackStore, this.storeDidChange);
    },
    storeDidChange(){
        this.setState({
            playing: PlaybackStore.getState().playing,
            episode: PlaybackStore.getState().currentEpisode
        });
    },
    play(){
        PlaybackActions.resume();
    },
    pause(){
        PlaybackActions.pause();
    }
});

module.exports = PlayBar;
