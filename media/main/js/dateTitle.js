!function(modelPageView){

"use strict"

var DateTitle = function( someDate ){
    var self = this;
    this.init(someDate);
    this.msg = ko.computed(function(){
        if(!modelPageView.objects.docInfo.today().sameDate(self.date)){
          return self.date.displayName() + ", Today";
        }

        if(!modelPageView.objects.docInfo.today().isTomorrow(self.date)){
          return self.date.displayName() + ", Tomorrow";
        }

        return self.date.displayName();
    });
}

DateTitle.prototype = {
    constructor: DateTitle

,    init: function(someDate){
      this.date = someDate;
      this.timeLineId = "s" + String(this.date.asInt());
    }

,    date_string: function(){
      return this.date.displayName();
    }

,    templateName: "datetmp"
}


modelPageView.dateTitleFactory = function(someDate){ return DateTitle(someDate) }

}(modelPageView)
