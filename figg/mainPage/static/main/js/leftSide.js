! function (modelPageView){
    "use strict";
    /*global console:false, modelPageView:false, ko:false, $:false, Sammy:false, alert:false*/
    var CAL = "cal";
    var TAG = "tag";
    var SERIES = "series";
    var VENUE = "venue";
    modelPageView.constants.cal = CAL;
    modelPageView.constants.tag = TAG;
    modelPageView.constants.series = SERIES;
    modelPageView.constants.venue = VENUE;


    function ProfileDetail(identifier, type){
        this.loaded = ko.observable(false);
        this.link = {};
        this.args = {};
        this.identifier = identifier;
        this.details = {};
        this.type = type;
        this.selected = ko.observable(false);
        var diseminator;


        if(type === CAL){
            diseminator = "/";
            this.link.trackingLink = diseminator + identifier + "/tracking";
        }

        if(type === TAG){
            diseminator = "/t/";
        }

        if(type === SERIES){
            diseminator = "/i/";
        }

        if(type === VENUE){
            diseminator = "/v/";
        }

        this.link.profileLink = "/f/tracking/get_profile/";
        this.link.eventLink = diseminator + identifier;
        this.link.trackerLink = diseminator + identifier + "/trackers";

        if(type != TAG){
            this.link.tagLink = diseminator + identifier + "/tags";
        }
        this.args[type] = identifier;

        this.load(this.link.profileLink, this.args);
    }

    ProfileDetail.prototype = {
        constructor: ProfileDetail,
        load: function(profileLink, args){
            var self = this;
            $.get(profileLink, args, function(data){
                self.details = data;
                self.selected(self.details.selected);
                console.log("we are loaded" + self.details.description);
                self.loaded(true);
            });
        },

        track: function(){
            var self = this;
            var args = {};
            args[this.type] = this.details.id;
            args["add"] = !this.selected();

            $.post("/f/tracking/select",  args, function(x){
                if (x === 1) {
                    alert("something wrong happened, please refresh the browser");
                } else {
                    self.selected(!self.selected());
                }
            });

        }

    };

    modelPageView.ProfileDetail = ProfileDetail;

}(modelPageView);