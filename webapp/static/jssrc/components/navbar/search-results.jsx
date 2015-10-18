const React = require("react");
const Link = require("react-router").Link;

const Image = require("../common/image.jsx");

const SearchResults = React.createClass({
    render(){
        const styles = {
            position:"absolute",
            top: "100%",
            left: 0,
            right: 0
        }
        return (
            <div className="bg-white border border-black m0 p0" styles={styles}>
                {this.getResults()}
            </div>
            )
    },
    getResults(){
        return this.props.results.map((result) => {
            const encodedUrl = encodeURIComponent(result.feedUrl);
            return (
                    <Link to="podcast" params={{splat: encodedUrl}} title={result.trackName} className="clearfix">
                        <div className="col col-2">
                            <Image src={result.artworkUrl600} />
                        </div>
                        <div className="col col-10">
                            <p><strong>{result.trackName}</strong></p>
                            <p>{result.artistName}</p>
                        </div>
                    </Link>
                )
        })
    }
});

module.exports = SearchResults;
