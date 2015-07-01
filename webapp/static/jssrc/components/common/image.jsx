const React = require("react");

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
        src = src || this.props.src;
        const width = this.refs.image.getDOMNode().offsetWidth;
        if(src.search("gravatar") >= 0){
            this.setState({src: src + "?s="+width});
            return;
        }

        if(src.search("graph.facebook.com") >= 0){
            this.setState({src: src+ "?width="+width});
            return
        }

        this.setState({src: "https://podato-images.appspot.com/"+width+"?url="+ src});
    }
});

module.exports = Image;
