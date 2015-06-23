const React = require("react");
const PodcastTile = require("./podcast-tile.jsx");
const Spinner = require("../common/spinner.jsx");

const PodcastGrid = React.createClass({
    render(){
        if(this.props.podcasts == void(0)){
            return <Spinner />
        }
        return (<div {...this.props}>
                {this.props.podcasts.map((podcast) => {
                    return <PodcastTile podcast={podcast} key={podcast.id} />
                })}
            </div>)
    }
});

module.exports = PodcastGrid;
