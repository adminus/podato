const React = require("react");

var Episode = React.createClass({
    render(){
        var published = new Date(this.props.episode.published);
        return (
            <div className="clearfix mxn1 py2 border-bottom border-silver" key={e.guid}>
                <div className="col col-2 px1">
                <Image src={this.props.episode.image || this.props.podcast.image} className="full-width" />
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
    }
});

module.exports = Episode;
