!function(modelPageView){
  "use strict";
  /*global console:false, modelPageView:false, ko:false, $:false, Sammy:false*/

  var MONTHLY = 0;
  var FORTNIGHTLY = 1;
  var WEEKLY = 2;


  function DateSection(date){
      this.date = date;
      this.url = modelPageView.utils.constructURL(this.date);
      this.occurances = ko.observable("");
  }

  DateSection.prototype = {
     constructor: DateSection
  }

  function DateLineManager(forDate, previous){
      this.init(forDate, previous)
  }

  DateLineManager.prototype = {
      constructor: DateLineManager,

      init: function(forDate, previous){
        var today = modelPageView.objects.docInfo.today();
        var width = $(window).width();
        var size = modelPageView.objects.docInfo.size;
        this.rangeType = size === "small" ? WEEKLY : size === "medium" ? FORTNIGHTLY : MONTHLY;
        this.forDate = ko.utils.unwrapObservable(forDate);
        this.dates = this.calcDates(this.forDate, this.rangeType, previous);
        this.occurancesLoad(this.forDate);
        var dates = this.dates;
        this.active = ko.observable(this.forDate);
      },

       goBack: function(andStreamHolder){
        console.log("going back");
        var earliest = this.dates[0].date;

        var newForDate = new Date(earliest.getFullYear(), earliest.getMonth(), earliest.getDate() - 1);
        console.log("for date was " + modelPageView.objects.docInfo.forDate());
        modelPageView.objects.docInfo.forDate(newForDate);
        modelPageView.objects.dateLineManager(new DateLineManager(newForDate, true));
        console.log("for date is now " + modelPageView.objects.docInfo.forDate());

        if(andStreamHolder){
        modelPageView.objects.streamHolder().refresh();
        $(window).scrollTop(150);
        console.log("going back");
        }
      },

      goForward: function(andStreamHolder){
        console.log("we're going forward");
        var latest = this.dates[this.dates.length -1].date
        var newForDate = new Date( latest.getFullYear(), latest.getMonth(), latest.getDate() + 1)
        modelPageView.objects.docInfo.forDate(newForDate)
        modelPageView.objects.dateLineManager(new DateLineManager(newForDate, false))
        if(andStreamHolder){
         modelPageView.objects.streamHolder().refresh()
        }
      }

      , calcDates: function(forDate, rangeType, previous){
        var startDate, endDate;

        if(rangeType === MONTHLY){
          startDate = new Date(forDate);
          startDate.setDate(1);
          endDate = new Date(startDate);
          endDate.setMonth(forDate.getMonth() + 1);
        }
        else if(rangeType === WEEKLY && !previous){
          startDate = forDate.getPreviousDay(1)
          endDate = new Date(startDate)
          endDate.setDate( endDate.getDate() + 7 )
        }
        else if(rangeType === WEEKLY && previous){
          endDate = new Date(forDate)
          endDate.setDate(endDate.getDate() + 1)
          startDate = new Date(endDate)
          startDate.setDate(startDate.getDate() -7 )
        }
        else if(rangeType === FORTNIGHTLY && previous){
          endDate = new Date(forDate)
          endDate.setDate(endDate.getDate() + 1)
          startDate = new Date(endDate)
          startDate.setDate(startDate.getDate() -14 )
        }
        else if(rangeType === FORTNIGHTLY && !previous){
          startDate = forDate.getPreviousDay(1)
          endDate = new Date(startDate)
          endDate.setDate( endDate.getDate() + 14)
        }
        else{
          throw "unknown range type"
        }

        var result = [];
        var i = startDate;
        while(i < endDate){
          result.push(new DateSection(i));
          var next = new Date(i);
          next.setDate(i.getDate() + 1);
          i = next;
        }

        return result;
      },

      registerJquery: function(element, data){
            $(element).tooltip({placement: "bottom"});
      },

      occurancesLoad: function(forDate){
          var self = this;
          var fromDate = new Date(forDate.getFullYear(), forDate.getMonth(), 1);
          var toDate = new Date(forDate.getFullYear(), forDate.getMonth() + 1, 1);
          var args = { "start_date": fromDate.asInt(), "end_date": toDate.asInt() };
          $.get("/!get_dateline/", args, function(data){
               if(data === 1){
                 alert("um something wrong has happened, please refresh your page");
               }
               else{

                 for(var d in data){
                   var found = ko.utils.arrayFirst(self.dates, function(x){return x.date.sameDate(createDate(d)) === 0});
                   var eventLength = data[d];
                   if(eventLength > 3) eventLength = 3;
                   var occurances = "";

                   for(var i = 0; i < eventLength; i++){
                      occurances += "*";
                   }

                   if(found && eventLength){
                     found.occurances(occurances);
                     }
                 }
               }
          });
      },

      otherMonth: function(forDate, add){
          return new Date(forDate.getFullYear(), forDate.getMonth() + add, 1);
      },

      getLink: function(someDate){
            var url = modelPageView.objects.utils.constructURL(someDate);
            return url;
      },

      activateDateSection: function(date){
          var first = ko.utils.arrayFirst(this.dates, function(x){
            return x.date.equalDate(date);
          });

          if(first){
            this.active(date);
          }
          else{
            if(date && this.active()){

              var month = date.getMonth();
              var activeMonth = this.active().getMonth();
              var year = date.getFullYear();
              var activeYear = this.active().getFullYear();


            if((month > activeMonth && year === activeYear) ||  year > activeYear){
                this.goForward();
            }
            else if((month < activeMonth && year === activeYear) ||  year < activeYear){
                this.goBack();
            }
          }
          }
      }
  };

  modelPageView.DateLineManager = DateLineManager;

}(modelPageView);
