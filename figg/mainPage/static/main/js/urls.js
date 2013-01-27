$script.ready(["sammy", "main", "eventHolder", "trackingHolder"], function () {
    "use strict";
    /*global console:false, modelPageView:false, ko:false, $:false, Sammy:false*/

    modelPageView.objects.streamHolder = ko.observable();
    modelPageView.objects.dateLineManager = ko.observable();
    modelPageView.objects.profileHolder = ko.observable();
    modelPageView.streamType = ko.observable();
    modelPageView.objects.sideBar = ko.observable();
    modelPageView.objects.docInfo.cal = ko.observable();
    modelPageView.objects.docInfo.tag = ko.observable();
    modelPageView.objects.docInfo.forDate(new Date());
    modelPageView.objects.eventCreator = ko.observable();
    console.log("running setup");

    var clean = function () {
        modelPageView.objects.streamHolder(null);
        modelPageView.objects.dateLineManager(null);
        modelPageView.objects.profileHolder(null);
        modelPageView.streamType(null);
        modelPageView.objects.sideBar(null);
        modelPageView.objects.docInfo.cal = null;
        modelPageView.objects.docInfo.tag = null;
        modelPageView.objects.docInfo.forDate(new Date());
        modelPageView.objects.eventCreator(null);
        $(window).scrollTop(0);
    };

    Sammy(function () {

        this.post("/!event_creator_from_json/", function(){
            console.log("posting from json");
            return false;
        });

        // logout, remove handlers and reload
        this.get("/!logout", function () {
            $(window).unload();
            window.location.href = "/!logout";
        });
        this.get("/about", function () {
            $(window).unload();
            window.location.href = "/about";
        });
        // show updates
        this.get("/#u", function () {
            clean();
            modelPageView.streamType("you");
            modelPageView.objects.profileHolder(new modelPageView.TrackingHolder("/f/tracking/all", {}));
            modelPageView.objects.dateLineManager(new modelPageView.DateLineManager(modelPageView.objects.docInfo.forDate));
            modelPageView.objects.userDetails.populate(modelPageView.objects.docInfo.user);
        });
        // show who you're following
        this.get("/#p", function () {
            clean();
            modelPageView.streamType("updates");
            modelPageView.objects.streamHolder(new modelPageView.updateHolder());
            modelPageView.objects.dateLineManager(new modelPageView.DateLineManager(modelPageView.objects.docInfo.forDate));
            modelPageView.objects.userDetails.populate(modelPageView.objects.docInfo.user);
        });
        // show search box
        this.get("/#s/", function () {
            clean();
            modelPageView.streamType("search");
            modelPageView.objects.docInfo.search = this.params['search'];
            modelPageView.objects.streamHolder(new modelPageView.SearchHolder());
            modelPageView.objects.dateLineManager(new modelPageView.DateLineManager(modelPageView.objects.docInfo.forDate));
            modelPageView.objects.userDetails.populate(modelPageView.objects.docInfo.user);
            console.log("setting streamType to " + modelPageView.streamType());
        });
        // show create box
        this.get("/#c/", function () {
            $script.ready(["jQueryUI", 'underscore'], function () {
                clean();
                modelPageView.objects.userDetails.populate(modelPageView.objects.docInfo.user);
                modelPageView.objects.eventCreator(new modelPageView.EventCreator());
                modelPageView.objects.dateLineManager(new modelPageView.DateLineManager(modelPageView.objects.docInfo.forDate));
                console.log("setting streamType to " + modelPageView.streamType());
            });
        });

        // show date
        this.get("/d/:year/:month/:day", function () {
            clean();
            modelPageView.streamType("stream");
            var forDate = new Date(this.params["year"], this.params["month"] - 1, this.params["day"]);
            modelPageView.objects.docInfo.forDate(forDate);
            modelPageView.objects.streamHolder(new modelPageView.EventHolder());
            modelPageView.objects.dateLineManager(new modelPageView.DateLineManager(modelPageView.objects.docInfo.forDate));
            modelPageView.objects.userDetails.populate(modelPageView.objects.docInfo.user);
            console.log("setting streamType to " + modelPageView.streamType());
        });

        // series page
        this.get("/i/:series/trackers", function () {
            clean();
            var series = this.params['series'];
            modelPageView.streamType("series");
            modelPageView.objects.sideBar(new modelPageView.ProfileDetail(series, "series"));
            modelPageView.objects.dateLineManager(new modelPageView.DateLineManager(modelPageView.objects.docInfo.forDate));
            modelPageView.objects.docInfo.series = series;
            modelPageView.streamType("series");
            modelPageView.objects.profileHolder(new modelPageView.TrackingHolder("/f/trackers", {"series": series}));
        });


        this.get("/i/:series", function () {
            clean();
            var series = this.params['series'];
            modelPageView.streamType("series");
            modelPageView.objects.sideBar(new modelPageView.ProfileDetail(series, "series"));
            modelPageView.objects.dateLineManager(new modelPageView.DateLineManager(modelPageView.objects.docInfo.forDate));
            modelPageView.objects.docInfo.series = series;
            modelPageView.streamType("series");
            modelPageView.objects.streamHolder(new modelPageView.EventHolder({
                series: series
            }));
        });


        this.get("/t/:tag/trackers", function () {
            clean();
            var tag = this.params['tag'];
            modelPageView.objects.sideBar(new modelPageView.ProfileDetail(tag, "tag"));
            modelPageView.objects.dateLineManager(new modelPageView.DateLineManager(modelPageView.objects.docInfo.forDate));
            modelPageView.objects.docInfo.tag = tag;
            modelPageView.streamType("tag");
            modelPageView.objects.profileHolder(new modelPageView.TrackingHolder("/f/trackers", {"tag": tag}));
        });

        // show tag page
        this.get("/t/:tag", function () {
            clean();
            var tag = this.params['tag'];
            modelPageView.objects.sideBar(new modelPageView.ProfileDetail(tag, "tag"));
            modelPageView.objects.dateLineManager(new modelPageView.DateLineManager(modelPageView.objects.docInfo.forDate));
            modelPageView.objects.docInfo.tag = tag;
            modelPageView.streamType("tag");
            modelPageView.objects.streamHolder(new modelPageView.EventHolder({tag: tag }));
        });

        this.get("/:cal/tracking", function () {
            clean();
            var cal = this.params['cal'];
            modelPageView.objects.sideBar(new modelPageView.ProfileDetail(cal, "cal"));
            modelPageView.objects.docInfo.user === cal ? modelPageView.streamType("you") : modelPageView.streamType("cal");
            modelPageView.objects.profileHolder(new modelPageView.TrackingHolder("/f/tracking/all", {"cal": cal}));
            modelPageView.objects.docInfo.forDate(new Date());
        });

        this.get("/:cal/trackers", function () {
            clean();
            var cal = this.params['cal'];
            modelPageView.objects.sideBar(new modelPageView.ProfileDetail(cal, "cal"));
            modelPageView.objects.docInfo.user === cal ? modelPageView.streamType("you") : modelPageView.streamType("cal");
            modelPageView.objects.profileHolder(new modelPageView.TrackingHolder("/f/trackers", {"cal": cal}));
            modelPageView.objects.docInfo.forDate(new Date());
        });

        this.get("/:cal/tags", function () {
            clean();
            var cal = this.params['cal'];
            modelPageView.objects.sideBar(new modelPageView.ProfileDetail(cal, "cal"));
            modelPageView.objects.docInfo.user === cal ? modelPageView.streamType("you") : modelPageView.streamType("cal");
            modelPageView.objects.profileHolder(new modelPageView.TrackingHolder("/f/tags", {"cal": cal}));
            modelPageView.objects.docInfo.forDate(new Date());
        });


        // show a calendar/date
        this.get("/:cal/d/:year/:month/:day", function () {
            clean();
            var cal = this.params['cal'];
            modelPageView.objects.sideBar(new modelPageView.ProfileDetail(cal, "cal"));
            modelPageView.objects.docInfo.user === cal ? modelPageView.streamType("you") : modelPageView.streamType("cal");
            modelPageView.objects.docInfo.forDate(new Date(this.params["year"], this.params["month"] - 1, this.params["day"]));
            modelPageView.objects.streamHolder(new modelPageView.EventHolder({
                cal: cal
            }));
            modelPageView.objects.dateLineManager(new modelPageView.DateLineManager(modelPageView.objects.docInfo.forDate));
            modelPageView.objects.userDetails.populate(cal);
            console.log("setting streamType to " + modelPageView.streamType()); 
        });
        // show calendar
        this.get("/:cal", function () {
            clean();
            var cal = this.params['cal'];
            modelPageView.objects.sideBar(new modelPageView.ProfileDetail(cal, "cal"));
            modelPageView.objects.docInfo.user === cal ? modelPageView.streamType("you") : modelPageView.streamType("cal");
            modelPageView.objects.docInfo.forDate(new Date());
            modelPageView.objects.docInfo.cal = this.params['cal'];
            modelPageView.objects.streamHolder(new modelPageView.EventHolder({
                cal: cal
            }));
            modelPageView.objects.dateLineManager(new modelPageView.DateLineManager(modelPageView.objects.docInfo.forDate));
            modelPageView.objects.userDetails.populate(cal);
            console.log("setting streamType to " + modelPageView.streamType());
        });
        // show stream
        this.get("/", function () {
            clean();
            modelPageView.streamType("stream");
            modelPageView.objects.streamHolder(new modelPageView.EventHolder());
            modelPageView.objects.dateLineManager(new modelPageView.DateLineManager(modelPageView.objects.docInfo.forDate));
            modelPageView.objects.userDetails.populate(modelPageView.objects.docInfo.user);
            console.log("setting streamType to " + modelPageView.streamType());
        });
    }).run();
    ko.applyBindings(modelPageView);
    $("body").animate({opacity:1}, 200);
});