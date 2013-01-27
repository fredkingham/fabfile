!function(modelPageView){
  "use strict";


  function UserDetails(){
    var self = this
    this.img = ko.observable()
    this.populate = function(x){
          self.getImg(x)
    }
  }

  UserDetails.prototype = {
    constructor: UserDetails

    , getImg: function(x){
       var d = new Date()
       var self = this
        $.get("/d/get_img", {username: x}, function(data){
         self.img(data)
       });
    }

  }

  modelPageView.objects.userDetails = new UserDetails()

/* singleton to carry all the users followers */
  function FollowerHolder(){
    this.followers = ko.observableArray();
    var self = this;
     $.get("/!get_invitees", function(dataRows){
          self.followers(dataRows);
     });
  }


  FollowerHolder.prototype = {
    constructor: FollowerHolder

    , get_details: function(usernames){
        return ko.utils.arrayFilter(this.followers(), function(x){ return $.inArray(x.name, usernames) !== -1 })
    }
    }

    modelPageView.objects.followerHolder = new FollowerHolder();

}(modelPageView);

!function(modelPageView){
  "use strict"
  var ModalModel = function(appear, getData){
    var self = this;
    this.modal_init(appear, getData);
    this.template = ko.observable("blank");
    this.name = "modelModal"
    this.ready = ko.observable(false);
  }

  ModalModel.prototype = {
      constructor: ModalModel

    , modal_init: function(){
        this.appear = ko.observable(false);
    }

    , open: function(){
        this.appear(true);
        $("#modal").modal('show')
    }

    , close: function(){
        this.appear(false);
        $('#modal').modal('hide')
    }
  }

  modelPageView.objects.modalModel = new ModalModel();

  var InviteRow = function(row, selected){
      var self = this;
      self.name = row.name;
      self.id = row.id;
      self.img = row.img;
      self.selected = ko.observable(selected);
      self.select = function(){ self.selected(!self.selected()); }
  }

  var InviteBox = function(appear, attendees){
    this.init();
    this.followers = ko.observableArray([]);
    this.populated = false;
  }


  InviteBox.prototype = {
    constructor: InviteBox

  , init: function(){
     this.attendees = ko.observableArray([]);
     this.result = null;
     this.callback = null;
     this.template = "inviteModal";
     this.closer = ko.observable(false);
    }

  , refreshSelected: function(){
    var self = this;
    var followers = modelPageView.objects.followerHolder.followers();
    self.followers([]);

    _.each(followers, function(x){ 
      return self.followers.push(new InviteRow(x, _.any(self.attendees(), function(y){
        return y === x.name;
      })));
    });
  }

  , populate: function(attendees, closer, callback){
    this.attendees(attendees());
    this.result = attendees;
    this.refreshSelected();
    this.closer = closer;
    this.callback = callback;
    modelPageView.objects.modalModel.template("inviteModal");
    modelPageView.objects.modalModel.open();
  }

  , invite: function(){
    var self = this;
    var result = _.filter(self.followers(), function(x){
      return x.selected();
    });

    var named_result = _.map(result, function(x){return x.name});

    this.result(named_result);

    if(this.callback){
        this.callback();
    }
    this.cancel();
  }

  , cancel: function(){
    this.attendees([]);
    this.result = null;
    modelPageView.objects.modalModel.close();
  }

  }

var LoginSignUpModal = function(){
}

LoginSignUpModal.prototype = {
  constructor: LoginSignUpModal

,  populate: function(){
    this.twitter = ko.observable()
    this.submitted = ko.observable(false);
    this.errorText = ko.observable();
    this.loading = ko.observable();
    modelPageView.objects.modalModel.template("signupModal");
    modelPageView.objects.modalModel.open();
  }

, cancel: function(){
    this.twitter("")
    this.errorText("")
    this.submitted(false)
    this.loading(false)
    modelPageView.objects.modalModel.close();
  }

, signUp: function(){
    var self = this;
    this.loading(true)

    if(!this.twitter() || !this.twitter().length){
      this.errorText("that doesn't look right, can you double check?")
      return false;
    }
    else{
      $.post("/!sign_up", { twitter: this.twitter() }, function(data){
        if(data.issue === 0){
          console.log("data is " + JSON.stringify(data))
          self.submitted(true)
          self.loading(false)
        }
        else{
          self.errorText("something wrong happend, please try again later")
        }
      })
    }
  }
}

modelPageView.objects.loginSignUpModal = new LoginSignUpModal()
modelPageView.decorators.loginRequired = function(func){
  if(modelPageView.objects.docInfo.user.length){
    func()
  }
  else{
    modelPageView.objects.loginSignUpModal.populate()
  }
}


var VenuePickerModal = function(){
  this.init();
}

VenuePickerModal.prototype = {
    constructor: VenuePickerModal

,   init: function(){
      this.venueId = ko.observable()
      this.venueName = ko.observable()
      this.possibleVenues = ko.observableArray([]);
      this.venueCreatorModal = ko.observable(false)
}

,     close: function(){
          modelPageView.objects.modalModel.close();
          // horrible hack
          $(".where").val("");
          this.refresh();
      }

,   add: function(){
    this.callBack(this.venueId(), this.venueName())
    modelPageView.objects.modalModel.close();
}

,   cancel: function(){
    this.venueId(false)
    this.venueName(false)
    modelPageView.objects.modalModel.close();
}

, getVenues: function(searchTerm, sourceArray){

    $.ajax({
        type: 'GET',
        url: '/!get_venues/',
        dataType: 'json',
        data: {
            startString: searchTerm,
            delay: .5
        },
        success: function(data) {
            var add = {"label": "add new venue", "id": 0, "func": function(){
              modelPageView.objects.venueCreatorModal.populate();
            }};
            data.push(add);
            sourceArray(data);
        }        
    });
  }

, selectVenue: function(x){
      this.venue(x);
  }

, template: "venuePickerModal"

, populate: function(callBack){
    modelPageView.objects.modalModel.template(this.template)
    modelPageView.objects.modalModel.open();
    this.callBack = callBack
  }
}

modelPageView.objects.venuePickerModal = new VenuePickerModal()


var VenueCreatorModal = function(){
    this.init();
}

  VenueCreatorModal.prototype = {
    constructor: VenueCreatorModal

,   init: function(){
      this.name = ko.observable();
      this.address = ko.observable();
      this.postcode = ko.observable();
      this.private = ko.observable();
      this.errorText = ko.observable();
      this.successText = ko.observable();
      this.template = "venueCreatorModal";
    }

,   populate: function(){
      modelPageView.objects.modalModel.template("venueCreatorModal");
      modelPageView.objects.modalModel.open();
    }

,    createVenue: function(){
        var self = this;

        if(!self.validate(this.name)){
            this.errorText("Please enter a name");
        }
        else if(!self.validate(this.address)){
            this.errorText("Please enter an address");
        }
        else if(!self.validate(this.postcode)){
            this.errorText("Please enter a postcode");
        }
        else{
            var params = {};
            params.name = this.name();
            params.address = this.address();
            params.postcode = this.postcode();
            params.private = this.private();
            $.post("/submit_venue", params, function(data){
              if(data > 0){
                self.errorText("ah didn't work, please refresh the page and try again")
              }
              else{
                self.successText("thanks venue added");
                _.delay(function(){ modelPageView.objects.modalModel.close() }, 500);
                self.successText("");
              }
            })
        }

      }

,     refresh: function(){
          this.name("");
          this.address("");
          this.postcode("");
          this.errorText("");
      }

,     close: function(){
          modelPageView.objects.modalModel.close();
          // horrible hack
          $(".where").val("");
          this.refresh();
      }

,     validate: function(field){
          return field() && $.trim(field()).length;
      }
  };

  var CancellerModal = function(){}

  CancellerModal.prototype = {

    constructor: CancellerModal

  , populate: function(event){
      this.id = event.id
      self.successText = ko.observable()
      self.errorText = ko.observable()
      modelPageView.objects.modalModel.template("eventCancellerModal");
      modelPageView.objects.modalModel.open();
  }

  , cancel: function(event){
     modelPageView.objects.modalModel.close()
  }

  , post: function(event){
      $.post("/!cancel_event/", {id: this.id}, function(data){
        if(data === 0){
            self.successText("ok, event cancelled");
            _.delay(function(){
              modelPageView.objects.modalModel.close();
              modelPageView.objects.streamHolder().refresh();
              self.successText("")
              }, 300);
        }
        else{
              self.errorText("ah didn't work, please refresh the page and try again")
        }
      })
  } 

};


  if("objects" in modelPageView){
    modelPageView.objects.inviteBox = new InviteBox();
  }
  else{
    modelPageView.objects = {inviteBox: new InviteBox()};
  }

    modelPageView.objects.venueCreatorModal = new VenueCreatorModal();
    modelPageView.objects.cancellerModal = new CancellerModal();

}(modelPageView);


!function(modelPageView){

  var Option = function(option){
    this.init(option);
  }

  Option.prototype = {
    constructor: Option

  , init: function(option){
      var self = this;
      self.optionType = option
      self.optionName = option

      if(option === "add" || option === "accept" || option === "add privately" || option === "accept privately"){
          self.action = self.add

      if(option === "add" || option === "accept") self.img = "main/img/startryouts/grey7.gif"
      if(option === "add privately" || option === "accept privately") self.img = "main/img/icons/private1.png"
      }

      else if(option === "remove" || option === "unable"){
        self.action = self.remove 
        self.img = "main/img/startryouts/red7.gif"
      }
      else if(option === "discuss") self.action = self.discuss 
      else if(option === "invite"){
        self.action = self.invite
        self.img = "main/img/icons/invite.png"
      }
      else if(option === "notes") self.action = self.getNotes
      else if(option === "edit") self.action = self.edit
      else if(option === "cancel"){
        self.action = self.cancel
        self.img = "main/img/startryouts/red7.gif"
      }
      else if(option === "show responses"){ 
        self.action = function(){ alert("we're still working on this") }
      }
      else throw "unknown option " + option;
    }

  , discuss: function(item, event) { 
    event.discuss.reveal(event.discuss);
  }

  , invite: function(item, event){  
      $("#modelView").modal('show');
      event.openInvites();
    }

  , remove: function(item, event){
      var self = this;
      var params = {action: self.optionType, event: event.id}
      $.post("/!event_option/", params, function(data){
          if(data === 1){
            alert("something wrong happened, please try again later");
          }
          else{
            event.optionHolder.stop_attending()
          }
      });
    }

  , add: function(item, event){
     var self = this;
     var params = {action: self.optionType, event: event.id}
     $.post("/!event_option/", params, function(data){
          if(data === 1){
            alert("something wrong happened, please try again later");
          }
          else{
            event.optionHolder.attend()
            if(self.isPrivate(self)) event.private(true);
          }
    });

    }

, edit: function(item, event){
    event.eventEditor.populate(event);
    event.eventEditor.show(true);
}

, cancel: function(item, event){
    modelPageView.objects.cancellerModal.populate(event)
}

, isPrivate: function(self){ return self.optionName === "add privately" || self.optionName === "accept privately" }
}

var OptionHolder = function(statuses, cancelled){
  this.init(statuses, cancelled)
}

OptionHolder.prototype = {
  constructor: OptionHolder

, statusConstants: {
    ADDED: 0,
    INVITED: 1,
    ACCEPTED: 2,
    SEND_INVITES: 3,
    UNABLE: 4,
    CANCELLED: 5,
    CREATOR: 6
  }

, cancel: new Option("cancel")
, accept: new Option("accept")
, acceptPrivately: new Option("accept privately")
, add: new Option("add")
, addPrivately: new Option("add privately")
, unable: new Option("unable")
, remove: new Option("remove")
, showResponses: new Option('show responses')
, invite: new Option('invite')

, init: function(statuses, cancelled){
    var self = this
    this.options = ko.observableArray([])
    var options = []
    var statusConstants = this.statusConstants
    self.statuses = ko.observableArray(statuses)
    self.creator = $.inArray(statusConstants.CREATOR, statuses) !== -1
    self.options = ko.computed(function(){
    var a = $.inArray(statusConstants.ADDED, self.statuses());

    var options = []
    if(cancelled){
        return [ self.remove ]
    }
    else{
      if($.inArray(statusConstants.INVITED, self.statuses()) !== -1){
        options = options.concat([self.accept, self.acceptPrivately, self.unable]);
      }
      else if($.inArray(statusConstants.ACCEPTED, self.statuses()) !== -1){
        options.push(self.unable);
      }
      else if($.inArray(statusConstants.ADDED, self.statuses()) !== -1 && $.inArray(statusConstants.CREATOR, self.statuses()) === -1){
        options.push(self.remove);
      }
      else if($.inArray(statusConstants.CREATOR, self.statuses()) !== -1){
        options.push(self.cancel);
      }
      else{
        options.push(self.add);
    }
    }
    options.push(self.invite);
    return options
   })

     self.attending = ko.computed(function(){
          return ko.utils.arrayFirst(self.statuses(), function(x){
            return $.inArray(x, [statusConstants.ADDED, statusConstants.ACCEPTED, statusConstants.ADD_PRIVATELY, statusConstants.ACCEPT_PRIVATELY]) !== -1
          }) !== null;
     })

    }

, attend: function(){
    var statuses = this.statuses()
    statuses.push(this.statusConstants.ADDED)
    this.statuses(statuses)
  }

, stop_attending: function(){
    var statuses = this.statuses()
    var self = this;
    var ADDED = this.statusConstants.ADDED
    var ACCEPTED = this.statusConstants.ACCEPTED
    this.statuses(ko.utils.arrayFilter(statuses, function(x){ return x !== ADDED && x !== ACCEPTED }))
  }

, toggle: function(){
      this.attending() ? this.stop_attending() : this.attend()
  }

}


var Event = function ( event ){
  this.init(event)
}

Event.prototype = {
  constructor: Event

, eventType: "populated"

, init: function( event ){
    var self = this;
    self.eventEditor = modelPageView.eventEditor();
    self.discuss = modelPageView.discussCreator(event);
    self.optionHolder;
    self.revealNotes = ko.observable(false);
    self.forInvites = ko.observableArray([]);
    self.showInvites = ko.observable(false);
    self.getNoteBox = function(){ 
        return modelPageView.noteCreator(self) 
    }

    self.noteDisplay = function(){
        var box = modelPageView.boxCreator();
        box.notes = ko.observable([])
        return box;
    }()

    self.invite = function(){
        var params = {names: self.forInvites(), event: self.id};
          $.post("/!invite", params, function(){
            modelPageView.objects.eventHolder.refresh();
          });
    }

    for(var i in event){
      if(i === "attending_status"){
        self.optionHolder = new OptionHolder(event[i], event.cancelled)
      }
      else if(i === "description" || i === "title"){
        this[i] = event[i] ? modelPageView.utils.enrichText(event[i]) : event[i]
      }
      else if(i === "venue" && event[i]){
        self.venue = modelPageView.venueDisplayFactory(event[i]);
      }
      else{
        this[i] = event[i];
      }
    }

    if(!("description" in event)){
        this.description = null
    }

    this.private = ko.observable(event.public !== 0);
    this.date = createDate(event.date);
    this.cal_details = ko.utils.arrayMap(event.from, function(x){ return new modelPageView.CalTag(x) });
    this.from = ko.observableArray(self.calculateFrom());
    this.attendeeHolder = modelPageView.attendeeHolderFactory(event.id)
  }

, edit: function(){
    this.eventEditor.populate(this);
    this.eventEditor.show(true);
}

, cancel: function(){
  modelPageView.objects.cancellerModal.populate(this)
}

, calculateFrom: function(){
      // we can seperate it into tags and cals and just get the unique ones... no point
      var result = [];

      ko.utils.arrayForEach(this.cal_details, function(x){
          if(x.cal){
           if(!ko.utils.arrayFilter(result, function(y){return y.cal === x.cal}).length){
            result.push(x)
          }
          }
          else if(!ko.utils.arrayFilter(result, function(y){ return !y.cal && x.tag === y.tag }).length){
            result.push(x)
          }
        });

      return result;
  }

, revealDiscuss: function(event){
    // event.noteDisplay.show(true);
    var self = event;
    $.get("/!get_notes/", {'id': self.id}, function(data){
        if(data === 1){
          alert("something wrong happened, please try again later");
        }
        else{
           self.discuss.notes(ko.utils.arrayMap(data, function(x){ return new Note(x) }));
           self.discuss.notesLoaded(true)
        }
    });

    self.discuss.reveal(this.discuss)
}

, removeFrom: function(calTag){
    this.cal_details = ko.utils.arrayFilter(this.from(), function(x){ 
      return !x.isRelated(calTag) 
    })

    this.from(this.calculateFrom());
  }

, addFrom: function(calTag){
    this.cal_details.push(calTag);
    this.from(this.calculateFrom());
  }

, closeNotes: function(item){
    item.showNotes(false);
  }

, openInvites: function(){
    this.showInvites(true);
    modelPageView.objects.inviteBox.populate(this.forInvites, this.showInvites, this.invite);
  }

, closeBox: function( data ){
    this.show(false);
  }
}

modelPageView.eventFactory = function(data){ return new Event(data) }

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
}

modelPageView.dateTitleFactory = function(someDate){ return new DateTitle(someDate) }

}(modelPageView)



