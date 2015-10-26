const React = require("react");
const ReactDOM = require('react-dom');
const Link = require("react-router").Link;
const ListenerMixin = require("alt/mixins/ListenerMixin");

const SearchActions = require("../../actions/search-actions");
const SearchStore = require("../../stores/search-store");

const SearchResults = require("./search-results.jsx");

const SearchBox = React.createClass({
    mixins: [ListenerMixin],
    componentWillMount(){
        this.listenTo(SearchStore, this.storeDidChange);
    },
    render(){
        const showResults = ((this.state.focus && this.state.results !== null) || this.state.fetching);
        const results = showResults ? <SearchResults results={this.state.results} fetching={this.state.fetching} resultClicked={this.resultClicked} /> : null;
        return (
            <div {...this.props} style={{padding:"0.5rem"}}>
                <input type="search" name="search" style={{height:"1.5rem", width:"100%"}} placeholder="Find great podcasts." ref="input"
                    onFocus={this.focus} onChange={this.change} onBlur={this.blur} />
                {results}
            </div>
        )
    },
    getInitialState(){
        return {
            query: "",
            results: null,
            changedSinceLastFetch: false,
            focus: false,
            fetching: false
        }
    },
    focus(){
        this.setState({focus: true});
    },
    blur(){
        setTimeout( () => this.setState({focus: false, results: null}));
    },
    change(){
        const query = ReactDOM.findDOMNode(this.refs.input).value.trim();
        this.setState({query: query});
        if(query.length > 3){
            if(!this.state.fetching){
                SearchActions.search(query);
                this.setState({fetching: true});
            }else{
                this.setState({changedSinceLastFetch: true});
            }
        }
    },
    storeDidChange(){
        const results = SearchStore.getResults();
        this.setState({results: results});
        if(this.state.changedSinceLastFetch){
            SearchActions.search(this.state.query);
            this.setState({changedSinceLastFetch: false});
        }else{
            this.setState({fetching: false})
        }
    },
    resultClicked(res){
        ReactDOM.findDOMNode(this.refs.input).blur()
        ReactDOM.findDOMNode(this.refs.input).value = res.trackName;
    }
});

module.exports = SearchBox;
