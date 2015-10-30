const React = require("react");
const ReactDOM = require("react-dom")

const Image = React.createClass({
    render(){
        var className = "button not-rounded " + (this.props.className || "");
        return (
            <img {...this.props} src={this.state.src} ref="image" alt={this.props.alth || ""} />
        );
    },
    getInitialState(){
        return {
            src:"data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7"
        }
    },
    componentDidMount(){
        this.setSrc();
    },
    componentWillReceiveProps(newProps){
        this.setSrc(newProps.src);
    },
    setSrc(src){
        src = src || this.props.src || "https://www.gravatar.com/avatar/205e460b479e2e5b48aec07710c08d50?f=y&d=identicon";
        const width = ReactDOM.findDOMNode(this.refs.image).offsetWidth;
        if(src.search("gravatar") >= 0){
            this.setState({src: src + "?s="+width + "&d=wavatar"});
            return;
        }

        if(src.search("graph.facebook.com") >= 0){
            this.setState({src: src+ "?width="+width});
            return
        }

        this.setState({src: "http://res.cloudinary.com/podato/image/fetch/w_"+width+"/"+ encodeURIComponent(src)});
    }
});

module.exports = Image;
