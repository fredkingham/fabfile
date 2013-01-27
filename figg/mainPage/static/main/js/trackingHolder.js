!function(modelPageView){
  "use strict";

var Attendee = function(x, calType){
    for(var i in x){
      this[i] = x[i];
    }

    this.type = calType;
    this.selected = ko.observable(x.selected);

this.select = function(){
	var self = this;
	var args = { add: !self.selected() };
	if (self.type === "cal") args["cal"] = self.id;
	if (self.type === "tag") args["tag"] = self.id;

	$.post("/f/tracking/select", args, function(data){
    if(data){
        alert("something wrong happened, please refresh the page");
      }
    else{
        self.selected(!self.selected());
        }
    });
};

this.remove = function(){
	var self = this;
	var args = {}
	if (self.type === "cal") args["cal"] = self.id
	if (self.type === "tag") args["tag"] = self.name
	$.post("f/tracking/remove", args, function(data){
	    if(data){
	      alert("something wrong happened, please refresh the page")
	    };
	});

};

};

function TrackingHolder(url, args){
	this.init(url, args)
}

TrackingHolder.prototype = {
  constructor: TrackingHolder


, init: function(url, args){
    this.loading = ko.observable(true)
    this.attendees = ko.observableArray([])
    this.load(url, args)
  }


, typeChange: function(indexFunc){
    var index = indexFunc()
    if(index === 0) return true
    var attendees = this.attendees()
	return attendees[index].type !== attendees[index -1].type
}

, remove: function(indexFunc){
	var index = indexFunc();
	var attendees = this.attendees();
	attendees[index].remove();
	attendees.splice(index, 1);
	this.attendees(attendees);
}

, load: function(url, args){
    var self = this;
    console.log("we are loading " + url);
    $.get(url, args, function(data){
      if(data === 1){
        alert("something wrong happened, please refresh the page and try again");
      }
      else{
        var attendees = [];
        var types = ["cal", "tag"];
        for(var i in types){
           attendees = attendees.concat(ko.utils.arrayMap(data[types[i]], function(x){return new Attendee(x, types[i])}));

        }
        self.attendees(attendees);
        self.title = data["title"]
        self.loading(false);
      }
    });
  }
}

modelPageView.TrackingHolder = TrackingHolder;


}(modelPageView);




