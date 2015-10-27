const React = require("react");
const Image = require("../common/image.jsx");
const ListenerMixin = require("alt/mixins/ListenerMixin");

const PlaybackActions = require("../../actions/playback-actions");
const PlaybackStore = require("../../stores/playback-store");

var Episode = React.createClass({
    mixins: [ListenerMixin],
    render(){
        var published = new Date(this.props.episode.published);
        return (
            <div className="clearfix mxn1 py2 border-bottom border-silver">
                <div className="col col-2 px1">
                    <Image src={this.props.episode.image || this.props.podcast.image} className="full-width" />
                    {this.getPlayButton()}
                </div>
                <div className="col col-10 px1 lh1">
                    <span className="h5 bold">{this.props.episode.title}</span>
                    <span className="silver inline-block">
                        <i className="ml1 el el-calendar" aria-label="published:"/>
                        <date dateTime={published.toISOString()}>{published.toLocaleDateString()}</date> <i className="ml1 el el-time" aria-label="duration:" /> {this.props.episode.duration}</span><br/>
                    <span>{this.props.episode.subtitle}</span>
                </div>
            </div>
        )
    },
    getInitialState(){
        return this.makeState();
    },
    componentWillMount(){
        this.listenTo(PlaybackStore, this.storeDidChange);
    },
    storeDidChange(){
        this.setState(this.makeState());
    },
    makeState(){
        const playingEpisode = PlaybackStore.getState().currentEpisode;
        return {
            episodePlaying: playingEpisode && playingEpisode.guid == this.props.episode.guid,
            playing: PlaybackStore.getState().playing
        };
    },
    getPlayButton(){
        if(this.state.episodePlaying && this.state.playing){
            return <a onClick={this.pause}><i className="el el-pause"></i> pause</a>
        }else{
            return <a onClick={this.play}><i className="el el-play"></i> play</a>
        }
    },

    play(){
        if(this.state.episodePlaying){
            PlaybackActions.resume();
        }else{
            PlaybackActions.playEpisode(this.props.episode);
        }
        return false;
    },

    pause(){
        PlaybackActions.pause();
        return false;
    }
});

module.exports = Episode;
