var swagger = require("swagger-client");
var config = require("config");
var utils = require("./utils");
var merge = require("merge");
var EventEmitter = require("eventemitter3");

var API = new EventEmitter();

// API.loaded is a promise that will be resolved as soon as the API is ready to be used.
API.loaded = new Promise(function(resolve, reject){
    //Clients call API.load to start loading the API. root should be the protocol and host to connect to.
    //client_id should be the client id used for authorization, scopes should be the requested scopes.
    API.load = function(root, client_id, scopes) {
        console.log("loading API.");
        root = root || config.get("DOMAIN")[0]

        //Set up the Swagger client
        var client = new swagger({
            url: root + "/api/swagger.json",
            success: function () {
                merge(API, client.apis);
                resolve();
            }
        });
        //Set up our authentication code.
        initPodatoAuth(root, client, client_id, scopes);
    }
});


function initPodatoAuth(root, client, client_id, scopes) {
    API.PodatoAuth = function () {
        this.authData = JSON.parse(localStorage.getItem("authData")) || {};
        this.client = {
            client_id: client_id,
            scopes: scopes
        }
        if (this.isAuthenticated()) {
            console.log("Detected existing session");
            API.emit("authenticated");
        }
    }

    API.PodatoAuth.prototype.login = function (authProvider) {
        var authorizeEndpoint = root + "/api/oauth/authorize";
        var authorize_url = authorizeEndpoint + utils.encodeQueryString({
            redirect_uri: root + "/api/oauth/js" + utils.encodeQueryString({
                origin: location.origin
            }),
            client_id: this.client.client_id,
            scope: this.client.scopes,
            provider: authProvider,
            grant_type: "implicit",
            response_type: "token"
        });
        var wleft = (window.outerWidth - 400)/2;
        var win = window.open(authorize_url, "Log In to Podato", "width=400,height=400,left="+wleft);
        this.checkWindowClose(win);

        if (!this._loginCallbackAttached) {
            window.addEventListener("message", this.onMessage.bind(this), false);
            this._loginCallbackAttached = true;
        }
    }

    API.PodatoAuth.prototype.onMessage = function (event) {
        if (event.origin === root) {
            if (event.data.access_token) {
                this.authData = event.data;
                this.authData.expires = new Date().getTime() + this.authData.expires_in * 1000;
                localStorage.setItem("authData", JSON.stringify(this.authData))
                API.emit("authenticated");
            }
        } else{
            console.log("Message from unknown origin: " + event.origin);
        }
    }

    API.PodatoAuth.prototype.checkWindowClose = function(win){
        var self = this;
        if (win.closed){
            if(!self.isAuthenticated()){
                API.emit("loginCancelled");
            }
        }else{
            setTimeout(() => {
                self.checkWindowClose(win);
            }, 500);
        }
    }

    API.PodatoAuth.prototype.isAuthenticated = function () {
        return this.authData.access_token && this.authData.expires > new Date().getTime();
    }

    API.PodatoAuth.prototype.logout = function(){
        this.authData = null;
        localStorage.authData = null;
        API.emit("unauthenticated");
    }

    API.PodatoAuth.prototype.apply = function (req) {
        req.headers.Authorization = "Bearer " + this.authData.access_token;
    }

    var auth = new API.PodatoAuth();
    client.clientAuthorizations.add("javascript", auth)
    API.login = auth.login.bind(auth);
    API.logout = auth.logout.bind(auth);
    API.isLoggedIn = auth.isAuthenticated.bind(auth);
    console.log("auth initialized");
}

//Takes an async result as returned by the api, and turns it into a Promise, to
//be resolved as soon as the job is done.
API.asyncResultToPromise = (asyncResult) => {
    console.log("starting to check for async result: "+asyncResult.id);

    var pollInterval = 500;
    return new Promise((resolve, reject) => {
        //This function returns true if the response indicates the job is done.
        var handleResponse = (resp) => {
            if(resp.obj.state == "SUCCESS"){
                    resolve(resp.obj);
                return true;
            }else if(resp.obj.state == "FAILURE"){
                reject(resp.obj);
                return true;
            }
            return false;
        }

        //If the job is already done, thee's no need to start polling.
        if(handleResponse(asyncResult)){
            return;
        }

        var intervalId = setInterval(() => {
            API.async.getAsync({asyncId: asyncResult.id}, (resp) => {
                console.log("Polling...");
                if (handleResponse(resp)){
                    clearInterval(intervalId);
                }
            });
        }, pollInterval);
    });
};

module.exports = window.API = API;
