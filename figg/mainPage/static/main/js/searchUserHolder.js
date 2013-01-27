!function(modelPageView){
  "use strict"

function UserSearchHolder(){
  this.users = ko.observableArray([])
  this.more = ko.observable(false)
  if(!modelPageView.objects.docInfo.search){
    throw("unable to inialise search, not search term")
  }

  this.searchTerm = modelPageView.objects.docInfo.search
  this.populate()
  this.loaded = ko.observable(false)
}

UserSearchHolder.prototype = {
  constructor: UserSearchHolder

  , populate: function(){
    var self = this
    $.get('/!search_users/', {'search_term': self.searchTerm}, function(data){
      if(1 === data){
        alert("something wrong happened please refresh the page")
      }
      else{
        self.users(data.users)
        self.more(data.more)
        self.loaded = ko.observable(true)
      }
    })
  }
}

modelPageView.userSearchHolder = UserSearchHolder

}(modelPageView);
