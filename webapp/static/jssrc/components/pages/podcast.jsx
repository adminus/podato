const React = require("react");

const Page = require("../common/page.jsx");
const Image = require("../common/image.jsx");
const SubscribeButton = require("../podcasts/subscribe-button.jsx");
const Episode = require("../podcasts/episode.jsx");

const CurrentUserStore = require("../../stores/current-user-store");
const PodcastsStore = require("../../stores/podcasts-store");

const PodcastsActions = require("../../actions/podcast-actions");

const Podcast = React.createClass({
    mixins: [CurrentUserStore.mixin, PodcastsStore.mixin],
    contextTypes: {router: React.PropTypes.func},
    render(){
        var episodes = this.getEpisodes();
        return (
            <Page>
                <div className="clearfix mxn2">
                    <div className="col col-3 p2 all-hide md-show">
                        <Image src={this.state.podcast.image} className="full-width" />
                        <p><SubscribeButton podcast={this.state.podcast.id} /></p>
                        <p><strong>by:</strong> {this.state.podcast.author}</p>
                        <p><strong>subscribers:</strong> {this.state.podcast.subscribers}</p>
                    </div>
                    <div className="col col-12 md-col-9 p2">
                        <h1 className="clearfix">{this.state.podcast.title}</h1>
                        <p className="md-hide"><SubscribeButton podcast={this.state.podcast.id}/></p>
                        <p className="md-hide"><strong>by:</strong> {this.state.podcast.author}</p>
                        <p className="clearfix"><Image src={this.state.podcast.image} className="left md-hide m1" style={{width:"10%"}} />{this.state.podcast.description}</p>
                        <hr />
                        {episodes}
                    </div>
                </div>
                <div className="clearfix mxn2">
                    <div className="col col-12 p2">
                        <p className="gray">{this.state.podcast.copyright}</p>
                    </div>
                </div>
            </Page>
        );
    },
    getEpisodes(){
        var eps = this.state.podcast.episodes.map((e) => {
            return (<Episode episode={e} podcast={this.state.podcast} />);
        });
        console.log(eps);
        return eps;
    },
    getInitialState(){
        return {currentUser: CurrentUserStore.getCurrentUser(), podcast:{
            title: "Loading ...",
            image: "https://podato.herokuapp.com/img/logo.png",
            episodes: []
        }};
    },
    componentWillMount(){
        this.setPodcast();
    },
    componentWillReceiveProps(){
        this.setPodcast();
    },
    storeDidChange(){
        this.setState({currentUser:CurrentUserStore.getCurrentUser()});
        this.setPodcast();
    },
    setPodcast(){
        var podcastId = this.context.router.getCurrentParams().splat;
        var podcast = PodcastsStore.getPodcast(decodeURIComponent(podcastId));

        if (!podcast){
            PodcastsActions.fetchPodcast(podcastId);
        }else{
            this.setState({podcast:podcast});
        }
    }
});

module.exports = Podcast;
