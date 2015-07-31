const React = require("react");

const Page = require("../common/page.jsx");
const Image = require("../common/image.jsx");
const SubscribeButton = require("../podcasts/subscribe-button.jsx");

const CurrentUserStore = require("../../stores/current-user-store");
const PodcastsStore = require("../../stores/podcasts-store");

const PodcastsActions = require("../../actions/podcast-actions");

const Podcast = React.createClass({
    mixins: [CurrentUserStore.mixin, PodcastsStore.mixin],
    contextTypes: {router: React.PropTypes.func},
    render(){
        var episodes = this.state.podcast.episodes.map((e) => {
            var published = new Date(e.published);
            return (
                <div className="clearfix mxn1 py2 border-bottom border-silver" key={e.guid}>
                    <div className="col col-2 px1">
                        <Image src={e.image || this.state.podcast.image} className="full-width" />
                    </div>
                    <div className="col col-10 px1 lh1">
                        <span className="h5 bold">{e.title}</span>
                        <span className="silver inline-block">
                            <i className="ml1 el el-calendar" aria-label="published:"/>
                            <date dateTime={published.toISOString()}>{published.toLocaleDateString()}</date> <i className="ml1 el el-time" aria-label="duration:" /> {e.duration}</span><br/>
                        <span>{e.subtitle}</span>
                    </div>
                </div>
            );
        });
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
