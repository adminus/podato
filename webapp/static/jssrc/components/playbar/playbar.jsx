const React = require("react");
const Link = require("react-router").Link;
const ListenerMixin = require("alt/mixins/ListenerMixin");

const Image = require("../common/image.jsx");

const PlaybackStore = require("../../stores/playback-store");

const PlayBar = React.createClass({
    mixins: [ListenerMixin],
    render(){
        if(!this.state.episode){
            return null;
        }
        return (
            <nav className="fixed bottom-0 left-0 right-0 bg-red white px4" style={{height:"2.5rem"}}>
                <div className="container flex flex-stretch">
                    <Image src={this.state.episode.image} style={{height: "2.5rem"}} />
                    <button className="button button-red"><i className="el el-backward" /></button>
                    <button className="button button-red"><i className="el el-play" /></button>
                    <button className="button button-red"><i className="el el-forward" /></button>
                </div>
            </nav>
        )
    },
    getInitialState(){
        return {
            episode: PlaybackStore.getState().currentEpisode
        }
    },
    componentWillMount(){
        this.listenTo(PlaybackStore, this.storeDidChange);
    },
    storeDidChange(){
        this.setState({
            episode: PlaybackStore.getState().currentEpisode
        });
    }
});

module.exports = PlayBar;
