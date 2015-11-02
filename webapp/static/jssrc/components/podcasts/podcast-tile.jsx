const React = require("react");
const Link = require("react-router").Link;

const Image = require("../common/image.jsx");

const PodcastTile = React.createClass({
    render(){
        return (<div className="col col-12 sm-col-6 md-col-2 px2">
                    <Link to={`/podcasts/${this.props.podcast.encoded_id}`} title={this.props.podcast.title} className="clearfix">
                        <div className="col col-2 md-col-12">
                            <Image src={this.props.podcast.image} alt="" className="full-width "/>
                        </div>
                        <div className="col col-10 md-col-12">
                            <p className="px1 overflow-hidden" style={{height: "3rem", textOverflow: "ellipsis", overflow: "hidden", WebkitBoxOrient: "vertical", display: "-webkit-box"}}>{this.props.podcast.title}</p>
                        </div>
                    </Link>
                </div>);
    }
});

module.exports = PodcastTile;
