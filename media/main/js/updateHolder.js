!function(modelPageView){
  "use strict"
  
  function enhanceUpdate(data){
    if("shareButton" in data){
        alert("something wrong has happened");
    }

    data.shareButton = ko.observable(false);
    data.sharedx = ko.observable(data.shared);
    data.date = createDate(data.date)

    data.setShareButton = function(x){
        data.shareButton(x);
    }

    data.share = function(){
      $.post("/share_note/", {id: data.note_id}, function(response){
        if(response === 1){
           var shared = data.sharedx() ? false : true;
           data.sharedx(shared);
        }
    });
    }

    if(data.event){
      data.event = modelPageView.eventFactory(data.event)

      if(data.type === "response" || data.type === "mention" || data.type === "comment"){ 
        data.event.noteDisplay.notes = ko.utils.arrayMap(data.notes, function(x){ 
          var note = new modelPageView.Note(x) 
          note.highlighted = data.note_id === x.note_id
          return note
        })

        data.event.noteDisplay.closeable = false;
        data.event.noteDisplay.show(true)
      }
    }

    if("event_date" in data) data["eventDate"] = createDate(data.event_date)
    if("date" in data) data["date"] = createDate(data.date)

    if("details" in data){
        if("detailButton" in data){
          alert("something wrong has happened");
        }

        data.detailButton = ko.observable(false);
        data.acceptedx = ko.observable(data.accepted)
        data.setDetailButton = function(x){
          data.detailButton(x);
        }

        data.accept = function(){
          $.post("/share_detail/", {id: data.detail_id}, function(response){
            if(response === 1){
               var accepted = data.acceptedx() ? false : true;
               data.acceptedx(accepted);
            }
          });
        }

    } 


    return data;
  }


  function UpdateHolder(){
    this.genericInit()
    this.updatingTop(false)
    this.streamType("updates")
    var self = this

    this.noEvents = ko.computed(function(){
        if(!self.events().length && !self.loading() && !modelPageView.objects.eventCreator()){
          return "no events have been added at this time for those people, select some more and we'll see how we do";
        }
          return "";
    });
  }

  UpdateHolder.prototype = jQuery.extend(true, {}, modelPageView.GenericHolder.prototype);

  $.extend(UpdateHolder.prototype, {
    constructor: UpdateHolder

    , loadTop: function(){
      throw("update manager can't load top")
    }

    , loadBottom: function(){
      if(!this.loadingMoreBottom){
        var self = this

        var events = self.events()
        var args = { id: events[events.length -1].id }
        $.post('/!read_notification/', args, function(data){
        if(1 === data){
          alert('something wrong happend, please refresh the page')
        }
        else{
           ko.utils.arrayForEach(data.notifications, function(x){ self.events.push(enhanceUpdate(x)) })
           self.events.sort( function(x, y){ return x.date.sameDate(y.date) * -1 })
           self.updatingBottom(data.more);
           self.loadingMoreBottom = false
        }
        })
      }
    }

    , populate: function(){
      var self = this;

      $.post('/!read_notification/', {}, function(data){
        if(1 === data){
          alert('something wrong happend, please refresh the page')
        }
        else {
          self.events(ko.utils.arrayMap(data.notifications, function(x){ return enhanceUpdate(x) }))
          self.events.sort( function(x, y){ return x.date.sameDate(y.date) * -1 })
          self.updatingBottom(data.more)
          self.loading(false);
        }
      })
      
    }

    , dateChange: function(indexFunc){
      var index = indexFunc()
      if(index === 0) return true

      var notifications = this.events()
      return notifications[index].date.sameDate(notifications[index -1 ].date) !== 0

    }

    , refresh: function(){
      this.updated(false)
      this.notifications([])
      this.populate()
    }
  })

modelPageView.updateHolder = UpdateHolder

}(modelPageView);
