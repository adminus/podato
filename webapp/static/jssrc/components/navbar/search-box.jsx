const React = require("react");
const Link = require("react-router").Link;
const ListenerMixin = require("alt/mixins/ListenerMixin");

const SearchActions = require("../../actions/search-actions");
const SearchStore = require("../../stores/search-store");

const SearchResults = require("./search-results.jsx");

const SearchBox = React.createClass({
    mixins: [ListenerMixin],
    componentWillMount(){
        this.listenTo(SearchStore, this.storeDidChange.bind(this));
    },
    render(){
        var results = false;
        if(this.state.focus && this.state.results && this.state.results.length > 0){
            results = <SearchResults results={this.state.results} fetching={this.state.fetching} />
        }
        return (
            <div style={{padding:"0.5rem"}}>
                <input type="search" name="search" style={{height:"1.5rem"}} placeholder="Find awesome podcasts." ref="input"
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
        this.setState({focus: false});
    },
    change(){
        const query = this.refs.input.getDOMNode().value.trim();
        this.setState({query: query});
        if(query.length > 3 && !this.state.fetching){
            SearchActions.search(query);
            this.setState({fetching: true})
        }
    },
    storeDidChange(){
        const results = SearchStore.getResults();
        this.setState({results: results});
    }
});

module.exports = SearchBox;