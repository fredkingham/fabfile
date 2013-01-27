
!function(modelPageView) {
  "use strict";


  var VenueDisplay = function(venueDetails) {
      this.init(venueDetails)
    }

  VenueDisplay.prototype = {
    constructor: VenueDisplay

    ,
    init: function(venueDetails) {
      this.show = ko.observable(false);
      this.title = venueDetails.title
      this.address = venueDetails.address
      this.lat = venueDetails.lat
      this.lng = venueDetails.lng
      this.link = "http://maps.google.com/?ie=UTF8&q=" + venueDetails.lat + "," + venueDetails.lng + "&z=19"
    }

    ,
    reveal: function(self) {
      self.show(true)
      var latlng = new google.maps.LatLng(self.lat, self.lng);
      var myOptions = {
        zoom: 15,
        center: latlng,
        mapTypeId: google.maps.MapTypeId.ROADMAP
      };
      var map = new google.maps.Map(document.getElementById("map_canvas"), myOptions);
      var marker = new google.maps.Marker({
        position: latlng,
        map: map,
        title: self.title
      });
    }

    ,
    close: function() {
      this.show(false);
    }
  };


  var Attendee = function(x) {
      this.name = x.name
      this.user_id = x.user_id
      this.img_normal = x.img_normal
      this.selected = ko.observable(x.selected)
      this.select = function() {

        $.post("/f/tracking/select", {
          cal: this.user_id,
          add: !this.selected()
        }, function(data) {
          if(data) {
            alert("something wrong happened, please refresh the page")
          } else {
            if(modelPageView.objects.streamHolder()) {
              modelPageView.objects.streamHolder().refresh()
            }
          }
        })

      }
    }

  var Tag = function(x) {
      this.name = x.name
      this.selected = ko.observable(x.selected)
      this.select = function() {
        $.post("/f/tracking/select", {
          tag: this.name,
          add: !this.selected()
        }, function(data) {
          if(data) {
            alert("something wrong happened, please refresh the page")
          } else {
            if(modelPageView.objects.streamHolder()) {
              modelPageView.objects.streamHolder().refresh()
            }
          }
        })
      }
    }

  var AttendeeHolder = function(eventId) {
      this.init(eventId)
    }

  AttendeeHolder.prototype = {
    constructor: AttendeeHolder

    ,
    init: function(eventId) {
      this.show = ko.observable(false)
      this.eventId = eventId
      this.reveal = $.proxy(this.display, this)
    }

    ,
    load: function() {
      var self = this
      this.loading = ko.observable(true)
      self.show(true);
      $.get("/!get_attending/", {
        id: self.eventId
      }, function(data) {
        self.attendees(ko.utils.arrayMap(data.attendees, function(x) {
          return new Attendee(x)
        }))
        self.tags(ko.utils.arrayMap(data.tags, function(x) {
          return new Tag(x)
        }))
        self.privatelyAttending(data.privately_added)
        self.loading(false)
      });

    }

    ,
    display: function() {
      this.attendees = ko.observableArray([])
      this.tags = ko.observableArray([])
      this.privatelyAttending = ko.observable(0)
      this.load()
    }

    ,
    closeBox: function() {
      this.attendees([])
      this.privatelyAttending(0)
      this.show(false)
    }
  }

  modelPageView.attendeeHolderFactory = function(id) {
    return new AttendeeHolder(id)
  };

  var Discuss = function(event) {
      this.initDiscuss(event);
    }

  Discuss.prototype = {
    constructor: Discuss

    ,
    initDiscuss: function(event) {
      if(event) {
        this.id = event.id;
      }

      this.show = ko.observable(false);
    }

    ,
    display: function(self, event_id) {
      $.get("/!get_notes/", {
        'id': event_id
      }, function(data) {
        if(data === 1) {
          alert("something wrong happened, please try again later");
        } else {
          self.notes(ko.utils.arrayMap(data, function(x) {
            return new modelPageView.Note(x)
          }));
          self.notesLoaded(true)
        }
      });

      $script.ready(["jQueryUI", 'underscore'], function() {
        self.description = ko.observable();
        var analysis = _.throttle(function() {
          self.analyseUsers(self)
        }, 5000);
        self.notes = ko.observableArray();
        self.notesLoaded = ko.observable(false);
        self.subscription = self.description.subscribe(analysis);
        self.showInvites = ko.observable(false);
        self.desc_invitees = ko.observableArray();
        self.selectedInvitees = ko.observableArray();
        self.invitees = ko.computed(function() {
          return _.compact(_.uniq(_.union(self.desc_invitees(), self.selectedInvitees())));
        });
        self.show(true);
      });
    }

    ,
    reset: function() {
      this.description("");
    },
    openInvites: function() {
      modelPageView.objects.inviteBox.populate(this.selectedInvitees, this.showInvites);
      this.showInvites(true);
    }

    ,
    closeBox: function() {
      this.subscription.dispose()
      this.description("");
      this.desc_invitees = ko.observableArray([]);
      this.selectedInvitees = ko.observableArray([]);
      this.show(false);
    }

    ,
    getAnalysisData: function() {
      return this.description();
    }

    ,
    analyseUsers: function(self) {
      var regex = /(?:\W|^)@(\w*)/g
      var analysisData = self.getAnalysisData();

      if(!analysisData || !analysisData.length) {
        return
      }
      var matches = _.map(analysisData.match(regex), function(x) {
        return $.trim(x).substr(1)
      });
      var new_ones = _.difference(matches, self.desc_invitees());
      var removed_ones = _.difference(self.desc_invitees(), matches);

      if(new_ones.length) {
        $.get("/!are_users", {
          uns: new_ones
        }, function(data) {
          if(data.length) {
            self.desc_invitees(_.uniq(_.difference(self.desc_invitees().concat(data), removed_ones)));
          } else {
            self.desc_invitees(_.difference(self.desc_invitees(), removed_ones));
          }
        });
      } else {
        self.desc_invitees(_.difference(self.desc_invitees(), removed_ones));
      }
    }

    ,
    post: function(self) {
      var self = this
      $.post("/!discuss_creator/", {
        description: this.description(),
        eventId: this.id,
        who: this.invitees()
      }, function() {
        self.show(false);
        modelPageView.objects.streamHolder().refresh();
      });
    }
  }


  var EventCreator = function(event) {
      this.initDiscuss(event);
      this.initEventCreator();
      this.display();
    }

  EventCreator.prototype = jQuery.extend(true, {}, Discuss.prototype);

  $.extend(EventCreator.prototype, {
    constructor: EventCreator

    ,
    initEventCreator: function() {
      var self = this;
      this.updatedDate = false;
      this.updatedTime = false;
      this.private = ko.observable(false);
      this.currentDate = modelPageView.objects.docInfo.today();
      this.returnedDate;
      this.eventDate = ko.observable();
      this.untilDate = ko.observable();
      this.returnedTime;
      this.eventTime = ko.observable();
      this.revealed = ko.observable(false);
      this.revealedDescription = ko.observable(false);
      this.overRiddenDate = ko.observable(false);
      this.venueId = ko.observable();
      this.venueName = ko.observable();
      this.repeatEvent = ko.observable();
      this.repeatUntil = ko.observable();
      this.errorText = ko.observable();
      this.successText = ko.observable();
      this.eventFocused = ko.observable(false);
      this.revealedRepeat = ko.observable(false)
      this.subscriptions = []
      self.imgUrl = ko.observable()
      self.imgId = ko.observable()
      self.loadingPreview = ko.observable(false)
      self.img = ko.observable()
      self.imgName = ko.observable()
      self.fileName = ko.computed(function() {
        return self.img() && !self.imgId ? self.img().replace(/^.*[\\\/]/, '') : ""
      })
      self.desc_invitees = ko.observableArray();
      self.selectedInvitees = ko.observableArray();

    }

    ,
    uploadPreview: function(files) {
      var self = this
      self.loadingPreview(true)
      var file = files[0]
      if(file.size > 20000000) {
        alert("that image is a bit too big for us, got anything smaller?")
      }
      var formData = new FormData();
      formData.append("img", file)
      $.ajax({
        url: "/!img_preview",
        type: 'POST',
        data: formData,
        cache: false,
        contentType: false,
        processData: false
      }).done(function(data) {
        if(data === "error") {
          alert("somethign wrong happened, please refresh the page")
          return
        }
        self.imgUrl(data.img_url)
        self.imgId(data.img_id)
      }).fail(function() {
        self.loadingPreview(false)
      })
    }

    ,
    cancelPreview: function(ce) {
      ce.img(null)
      ce.imgId(null)
      ce.imgUrl(null)
      ce.loadingPreview(null)
    }


    ,
    togglePrivate: function() {
      this.private(!this.private())
    }

    ,
    toggleRepeat: function() {
      this.revealedRepeat(!this.revealedRepeat())
    }

    ,
    reveal: function() {
      //if(modelPageView.objects.docInfo.size !== "large"){
      window.location.href = "/#c/"
    }

    ,
    display: function() {
      var self = this;
      $script.ready(["jQueryUI", 'underscore'], function() {
        self.showInvites = ko.observable(false);

        self.eventFocused(true);
        self.description = ko.observable("");
        self.title = ko.observable("");
        var analysis = _.throttle(function() {
          self.analyse(self)
        }, 500);
        self.subscriptions.push(self.title.subscribe(analysis));
        self.errorTitle = ko.observable(false)
        self.errorDescription = ko.observable(false)
        self.errorDate = ko.observable(false)
        self.subscriptions.push(self.description.subscribe(analysis))
        self.invitees = ko.computed(function() {
          return _.compact(_.uniq(_.union(self.desc_invitees(), self.selectedInvitees())));
        });
        self.show(true);
      })

      self.invitees_details = ko.computed(function() {
        return modelPageView.objects.followerHolder.get_details(_.compact(_.uniq(_.union(self.desc_invitees(), self.selectedInvitees()))))
      })
    }

    ,
    getVenue: function() {
      var self = this;
      var assignVenue = function(x, y) {
          self.venueId(x);
          self.venueName(y)
        }
      this.venuePickerModal = modelPageView.objects.venuePickerModal
      this.venuePickerModal.populate(assignVenue);
    }

    ,
    getAnalysisData: function() {
      return this.title() + " " + this.description();
    }

    ,
    analyse: function(self) {
      self.analyseUsers(self);
      self.analyseDateTime(self);
    },
    analyseDateTime: function(self) {
      var updatedDate = self.eventDate() && self.eventDate() !== self.returnedDate;
      var updatedTime = self.eventTime() && self.eventTime() !== self.returnedTime;

      if(!self.updatedDate || !self.updatedTime) {
        $.post("/!event_info_process", {
          data: self.getAnalysisData(),
        }, function(response) {
          if("date" in response && !updatedDate) {
            self.returnedDate = createDate(response.date);
            self.eventDate(self.returnedDate);
          }
          if("time" in response && !updatedTime) {
            self.returnedTime = response.time;
            self.eventTime(self.returnedTime);
          }
        });
      }

    }


    ,
    errorChecks: function() {
      var flawed = false
      var titleLength = this.title().length
      var descriptionLength = this.description().length
      var self = this
      var titleSubscription = function() {
          self.errorTitle(false)
          self.errorText("")
        }
      var descriptionSubscription = function() {
          self.errorDescription(false)
          self.errorText("")
        }

      if(!titleLength) {
        this.errorText("please enter a name for your event");
        this.errorTitle(true)
        flawed = true
        this.subscriptions.push(self.title.subscribe(titleSubscription))
      } else if(titleLength > 100) {
        this.errorTitle(true)
        this.errorText("please can you leave a shorter title")
        flawed = true
        this.subscriptions.push(self.title.subscribe(titleSubscription))
      } else if(descriptionLength > 250) {
        this.errorDescription(true)
        this.errorDescription("please can you leave a shorter description")
        this.subscriptions.push(self.title.subscribe(descriptionSubscription))
        flawed = true
      } else if(!this.eventDate() || this.eventDate().getFullYear() === 1970) {
        this.errorText("please enter a date for your event");
        this.errorDate(true)
        flawed = true
      }

      return flawed
    }

    ,
    post: function(self) {
      var self = this;
      // return false
      if(!self.errorChecks()) {
        // if there is an img and no imgURL that means we haven't had time 
        // to process the image, let's just do a plain post (I know
        // we could use an ajax post for some browsers, but its not biggy
        if(self.img() && !self.imgUrl) {
          console.log("are we returning true?")
          return true
        }

        if(self.revealedRepeat()) {
          // var repeatEvent = $.inArray(self.repeatEvent(), ['HOURLY', 'DAILY', 'WEEKLY', 'MONTHLY'])
          var repeatEvent = self.repeatEvent()
          if(repeatEvent === -1) {
            alert("something wrong happened, please refresh the page and try again")
          }

          var repeatUntil = self.repeatUntil()

        } else {
          var repeatEvent = undefined
          var repeatUntil = undefined
        }

        $.post("/!event_creator_from_json/", {
          title: self.title(),
          description: self.description(),
          invited: self.invitees().join(),
          event_date: self.eventDate().asInt(),
          event_time: self.eventTime(),
          event_venue: self.venueId(),
          public: !self.private(),
          repeat_regularity: repeatEvent,
          repeat_until: repeatUntil,
          img_id: self.imgId()
        }, function(data) {
          if(data === 0) {
            self.errorText("");
            console.log("are we going here?")
            self.successText("thanks, added");
            self.removeSubscriptions()
            _.delay(function() {
              self.closeBox();
              if(modelPageView.objects.streamHolder()){
                  modelPageView.objects.streamHolder().refresh()
              }
              self.initEventCreator();
              self.closeBox()
            }, 300);
          } else {
            self.errorText(data);
          }
        });
      }
      return false
    }

    ,
    toggleDescription: function() {
      this.revealedDescription(!this.revealedDescription());
    }

    ,
    removeSubscriptions: function() {
      ko.utils.arrayMap(this.subscriptions, function(x) {
        x.dispose()
      })
    }

    ,
    closeBox: function() {
      this.removeSubscriptions()
      this.title("");
      this.description("");
      this.show(false);
      this.errorText("");
      this.errorDescription("");
      this.errorDate("");
      window.location.href = "/"
    }


  });

  modelPageView.EventCreator = EventCreator;

  var Box = function() {
      this.initBox()
    }

  Box.prototype = {
    constructor: Box

    ,
    initBox: function() {
      this.show = ko.observable(false);
      this.loaded = ko.observable(false);
      this.closeable = true;
    }

    ,
    close: function() {
      this.show(false)
    }
  }


  var EventEditor = function(event) {
      this.initBox();
      this.initDiscuss(event);
      this.initEventCreator(event);
    }

  EventEditor.prototype = jQuery.extend(true, {}, EventCreator.prototype); /* remove this and change the discuss to inherit from box if this pattern works */
  $.extend(EventEditor.prototype, jQuery.extend(true, {}, Box.prototype));

  $.extend(EventEditor.prototype, {
    constructor: EventEditor

    ,
    populate: function(event) {
      var regex = /<.*?>/g
      var self = this
      this.id = event.id
      this.updatedDate = true;
      this.updatedTime = event.time ? true : false;
      this.eventTime(event.time);
      this.id = event.id
      this.eventDate = ko.observable(event.date);
      this.title = ko.observable(event.title.replace(regex, ""));
      this.venueName = event.venue ? event.venue.title : false;
      self.errorTitle = ko.observable(false)
      self.errorDescription = ko.observable(false)
      self.errorDate = ko.observable(false)

      if(event.description) this.description = ko.observable(event.description.replace(regex, ""))
      else this.description = ko.observable("")

      var revealDescription = (event.description || event.venue) ? true : false;
      this.revealedDescription(revealDescription);
      this.img = event.img
      this.private = ko.observable(event.private);
      this.event = event
      this.desc_invitees = ko.observableArray();
      this.selectedInvitees = ko.observableArray();
      this.invitees = ko.computed(function() {
        return _.compact(_.uniq(_.union(self.desc_invitees(), self.selectedInvitees())));
      });
    }

    ,
    post: function(self) {
      var self = this;

      if(!self.errorChecks()) {
        $.post("/!event_editor/", {
          title: self.title(),
          description: self.description(),
          invited: self.invitees(),
          event_date: self.eventDate().asInt(),
          event_time: self.eventTime(),
          venue: self.venueName,
          public: true,
          repeatEvent: self.repeatEvent(),
          repeatUntil: self.repeatUntil(),
          event: self.id
        }, function(data) {
          if(data === 0) {
            self.errorText("");
            self.successText("thanks, changed");
            self.removeSubscriptions()
            self.revealed(false);
            _.delay(function() {
              modelPageView.objects.streamHolder().refresh();
            }, 300);
          } else {
            self.errorText(data);
          }
        });
      }
    }
  });

  modelPageView.canceller = function() {
    return new Canceller()
  }

  modelPageView.noteCreator = function(event) {
    return new Discuss(event);
  }

  modelPageView.boxCreator = function() {
    return new Box();
  }

  modelPageView.eventEditor = function() {
    return new EventEditor()
  }


  modelPageView.discussCreator = function(event) {
    return new Discuss(event)
  }
  modelPageView.venueDisplayFactory = function(venueDetails) {
    return new VenueDisplay(venueDetails)
  }

  var Note = function(row) {
      this.init(row)
    }

  Note.prototype = {
    constructor: Note

    ,
    init: function(row) {
      var self = this;
      this.shareButton = ko.observable(false)
      this.sharedx = ko.observable(row.shared)
      this.highlighted = false
      for(var i in row) this[i] = row[i]

      if("details" in row) {
        if("detailButton" in row) {
          alert("something wrong has happened");
        }

        self.detailButton = ko.observable(false);
        self.acceptedx = ko.observable(row.accepted)
        self.setDetailButton = function(x) {
          self.detailButton(x);
        }

        self.accept = function() {
          $.post("/share_detail/", {
            id: self.detail_id
          }, function(response) {
            if(response === 1) {
              var accepted = self.acceptedx() ? false : true;
              self.acceptedx(accepted);
            }
          });

        }

      }
    }

    ,
    setShareButton: function(x) {
      this.shareButton(x)
    }

    ,
    share: function() {
      var self = this;

      $.post("/share_note/", {
        id: self.note_id
      }, function(response) {
        if(response === 1) {
          var shared = self.sharedx() ? false : true;
          self.sharedx(shared);
        }
      });
    }

  }

  modelPageView.Note = Note

}(modelPageView);