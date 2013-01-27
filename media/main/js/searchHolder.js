!
function(modelPageView) {
  "use strict"

  var SearchHolder = function() {
      var self = this
      if(!modelPageView.objects.docInfo.search) {
        throw("unable to inialise search, not search term")
      }

      this.searchTerm = modelPageView.objects.docInfo.search
      this.genericInit()

      this.noEvents = ko.computed(function() {
        if(!self.events().length && !self.loading() && !modelPageView.objects.eventCreator()) {
          return "we couldn't find any events that matched that search term";
        }
        return "";
      });
    }

  SearchHolder.prototype = jQuery.extend(true, {}, modelPageView.GenericHolder.prototype);

  $.extend(SearchHolder.prototype, {
    construct: SearchHolder

    ,
    loadBottom: function() {
      var self = this;
      var events = self.events()
      var event = events[events.length - 1]
      var args = {
        search_term: self.searchTerm,
        startId: event.id,
        up: false
      }
      var lastId = event.id
      $.get('/!search_term/', args, function(data) {
        if(1 === data) {
          alert("something wrong happened please refresh the page")
        } else {
          ko.utils.arrayForEach(data.events, function(x) {
            self.events.push(modelPageView.eventFactory(x))
          })
          self.events.sort(function(x, y) {
            return x.date.sameDate(y.date)
          })
          self.updatingBottom(data.more)
          self.loadingMoreBottom = false
        }
      })
    }

    ,
    loadTop: function() {
      var self = this

      if(!self.loadingMoreTop) {

        self.loadingMoreTop = true

        var args = {}

        args.search_term = self.searchTerm

        var events = self.events()
        args.up = true

        if(events.length) {
          var event = events[0]
          args.endId = event.id
          var id = "#" + $("#events").find(".event").first().attr("id");
        } else {
          args.end_date = modelPageView.objects.docInfo.forDate().asInt()
          var id = "#noEvents"
        }

        $.get("/!search_term/", args, function(data) {
          if(data === 1) {
            alert("please try again later");
          } else {
            var before = $(id).offset().top - $(document).scrollTop();
            ko.utils.arrayForEach(data.events, function(x) {
              self.events.push(modelPageView.eventFactory(x))
            })
            self.events.sort(function(x, y) {
              return x.date.sameDate(y.date)
            })
            self.updatingTop(data.previous);
            var after = $(id).offset().top
            $(document).scrollTop(after - before)
            setTimeout(function() {
              self.loadingMoreTop = false
            }, 500)
          }
        })
      }
    }

    ,
    populate: function() {
      var self = this;
      var args = {
        start_date: modelPageView.objects.docInfo.forDate().asInt()
      }
      args["search_term"] = self.searchTerm;

      $.get('/!search_term/', args, function(data) {
        if(1 === data) {
          alert("something wrong happened please refresh the page")
        } else {
          self.events(ko.utils.arrayMap(data.events, function(x) {
            return modelPageView.eventFactory(x)
          }))
          self.events.sort(function(x, y) {
            return x.date.sameDate(y.date)
          })
          self.updatingBottom(data.more);
          self.updatingTop(data.previous);
          self.loading(false)
        }
      })
    }
  })

  modelPageView.SearchHolder = SearchHolder;

}(modelPageView);