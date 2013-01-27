$script.ready(["main"], function(){
              
!function(modelPageView){
"use strict";

function EventHolder(calTag){
  var self = this;
  this.loading = ko.observable(true);
  if(calTag){
    this.cal = calTag.cal;
    this.tag = calTag.tag;
    this.series = calTag.series;
  }
  this.genericInit();
  this.init();
}

EventHolder.prototype = jQuery.extend(true, {}, modelPageView.GenericHolder.prototype);

$.extend(EventHolder.prototype, {
      constructor: EventHolder

,     init: function(){
        var self = this;
        this.noEvents = ko.computed(function(){
            if(!self.events().length && !self.loading() && !modelPageView.objects.streamHolder()){
              return "no events have been added at this time for those people, select some more and we'll see how we do";
            }
              return "";
        });
      }

,     loadBottom: function(){
          if(!this.loadingMoreBottom)
            {
            var self = this
            var args = self.getPopulateArgs()
            var events = self.events()
            var event = events[events.length -1]

            if(event.eventType != "empty"){
            args.start_key = event.key
            }
            else{
              args.start_date = event.date
            }

            args.up = false;
            self.loadingMoreBottom = true

            $.get("/!get_all_events", args, function(data){
              if(data === 1){
                alert("please try again later");
              }
              else{
                  self.addEvents(data.events, self);
                  self.updatingBottom(data.more);
                  self.loadingMoreBottom = false
                  self.resetDateLine()
                }
              });
            }
      }

,     loadTop: function(){
          var self = this

          var args = {}
          if(!self.loadingMoreTop){
           self.loadingMoreTop = true

          if(this.cal) args.cal = this.cal
          if(this.tag) args.tag = this.tag
          if(this.series) args.series = this.series

          var events = ko.utils.arrayFilter(self.events(), function(x){
              return x.eventType != "empty"
          })
          args.up = true;

          if(events.length){
            var event = events[0]

            if(event.key){
              args.end_key = event.key
            }
            else{
              args.end_date = event.date.asInt()
            }

            var id = "#" + $("#events").find(".event").first().attr("id");
          }
          else{
            args.end_date = modelPageView.objects.docInfo.forDate().asInt()
            var id = "#noEvents"
          }

          $.get("/!get_all_events", args, function(data){
            if(data === 1){
              alert("please try again later");
            }
            else{
                var before = $(id).offset().top - $(document).scrollTop();
                self.addEvents(data.events, self);
                self.updatingTop(data.previous);
                var after = $(id).offset().top
                $(document).scrollTop(after - before)
                setTimeout(function(){ self.loadingMoreTop = false}, 300)
                self.resetDateLine()
             }
            });
          }
      }

,     compareEvents: function(x, y){
        if(x.key && y.key) return x.key > y.key ? 1 : -1
        return x.date > y.date ? 1 : -1
      }

,     removeAll: function(){
        this.events([]);
      }

,     removeFrom: function(event, calTag){
        event.removeFrom(calTag);
        this.cleanEvents();
      }


,     cleanEvents: function(){
          var self = this;
          var allEvents = ko.utils.arrayFilter(self.events(), function(x){ 
            return x.eventType !== "empty" && x.from().length;
          });

          this.events(allEvents)
      }

,     removeEvents: function(calTag, self){
          var allEvents = self.events();
          for(var index in allEvents){
            var event = allEvents[index];
            event.removeFrom(calTag);
          }
      }

  , addEmpty: function(){
      var first, forDate = modelPageView.objects.docInfo.forDate()
      first = ko.utils.arrayFirst(this.events(), function(x){
          return x.date.equalDate(forDate)
      })

      if(!first){
          this.events.push({ date: forDate, eventType: "empty" })
      }
    }

,     addEvents: function(data, self){
              ko.utils.arrayForEach(data, function(item){
                
                var sameEvent = ko.utils.arrayFirst(self.events(), function(x){
                    return x.id === item.id
                });

                if(sameEvent){
                  var calTags = ko.utils.arrayMap(item.from, function(x){ new modelPageView.CalTag(x) });

                  ko.utils.arrayForEach(calTags, function(x){ sameEvent.cal_details.push(x) });

                  var toAdd = ko.utils.arrayFilter(item.from, function(x){ 
                    return ko.utils.arrayFilter(sameEvent.from(), function(y){
                          !y.sameCal(x)
                          }).length});

                  ko.utils.arrayForEach(toAdd, function(x){ sameEvent.push(x) });
                }
                else{
                var event = modelPageView.eventFactory(item);
                self.events.push(event);

                var event_in = ko.utils.arrayFirst(self.events(), function(x){
                    return x.id === event.id
                });
                }

              });

              this.addEmpty(this.events)
              var events = this.events()
              events.sort(self.compareEvents)
              this.events(events)
              self.resetDateLine();
      }

,     dateChange: function(indexFunc){
        var index = indexFunc()
        if(index === 0) return true
        var events = this.events()
        return events[index].date.sameDate(events[index -1].date) !== 0
      }

,     getPopulateArgs: function(){
          var args = {}
          args.start_date = modelPageView.objects.docInfo.forDate().asInt()

          if(this.cal) args.cal = this.cal
          if(this.tag) args.tag = this.tag
          if(this.series) args.series = this.series
          return args
      }

,     populate: function(){

        var self = this;
        self.loading(true);
        console.log("this.tags = " + this.tag)
        var args = self.getPopulateArgs();
        console.log("args are " + JSON.stringify(args))

        $.get("/!get_all_events", args, function(data){
          if(data === 1){
            alert("please try again later");
          }
          else{
              self.addEvents(data.events, self);
              self.loading(false);
              self.updatingBottom(data.more);
              self.updatingTop(data.previous);
            }
          });
        }



,     refresh: function(){
          this.removeAll();
          this.populate();
      }

,     resetDateLine: function(){
          modelPageView.objects.dateLineSpy.refresh()
      }

})

modelPageView.EventHolder = EventHolder

}(modelPageView)
})
