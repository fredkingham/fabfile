
function StarterFormViewModal(){
  this.twitter = ko.observable();
  this.post_form = function(form){
    if($("#sign-in-form").valid()){
      var post_data = ko.toJS({twitter: this.twitter});
      $.post("/!sign_up", post_data, function(data){
        if(!"issue" in data){
          $("#sign-up-error").text("something wrong happened, please refresh the page");
        }
        else if(data.issue){
          $("#sign-up-error").text(data["val"]);
        }
        else{
          $("#sign-up-success").text(data["val"]);
          $("#sign-up-error").text("");
        }
      });
    }
  };
}

ko.applyBindings(new StarterFormViewModal());
