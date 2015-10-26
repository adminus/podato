const React = require("react");
const Link = require("react-router").Link;

const Image = require("../common/image.jsx");
const Spinner = require("../common/spinner.jsx");


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
                <div className="clearfix" style={{display: this.props.fetching ? "block": "none"}}>
                    <div className="col col-12 center">
                        <Spinner />
                    </div>
                </div>
                {this.getResults()}
            </div>
            )
    },
    getResults(){
        if(this.props.results != null && this.props.results.length == 0){
            return (
                <p>Nothing found</p>
            )
        }
        return (this.props.results || []).map((result) => {
            const encodedUrl = encodeURIComponent(result.feedUrl);
            return (
                    <Link to={`/podcasts/${encodedUrl}`} title={result.trackName} className="clearfix" key={encodedUrl}
                        onMouseDown={this.resultClicked} onClick={this.afterResultClicked.bind(this, result)}>
                        <div className="col col-2">
                            <Image src={result.artworkUrl600} className="full-width" />
                        </div>
                        <div className="col col-10">
                            <p><strong>{result.trackName}</strong></p>
                            <p>{result.artistName}</p>
                        </div>
                    </Link>
                )
        })
    },
    resultClicked(e){
        console.log("resultClicked called");
        e.preventDefault();
    },
    afterResultClicked(r, e){
        console.log("afterResultClicked called");
        if(this.props.resultClicked){
            this.props.resultClicked(r);
        }
    }
});

module.exports = SearchResults;
