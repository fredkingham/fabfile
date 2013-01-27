!function(modelPageView){
  "use strict"

var SelectableCalTag = function ( calTag ){
  this.init(calTag)
  this.initMore(calTag);
}

SelectableCalTag.prototype = modelPageView.CalTag.prototype

$.extend(SelectableCalTag.prototype, {
  constructor: SelectableCalTag

, initMore: function( calTag ){
    this.selected = ko.observable(calTag.selected);
    this.revealed = ko.observable(calTag.revealed);
  }

, revealable: function(){
  return this.type < 2;
  }
, select: function(){
    this.selected(!this.selected());
  }

, reveal: function(callBack){
    var args = {calType: this.calType, cal: this.cal, tag: this.tag};
    var local_reveal = this.revealed

    $.post("/f/reveal_cal", args, function(data){
      if(data === 0){
        local_reveal(!local_reveal()); 
        if(callBack){
            callBack();
        }
      }
      else{
        alert("something wrong happened, please refrest the page and try again");
      }
    });
  }

, getTemplate: function(){
    if(this.type === 0){
      return "calType";
    }

    if(this.type === 1){
      return "cal";
    }

    return "tag";
  }
});

function ProfileHolder(){ this.init() }

ProfileHolder.prototype = {
  constructor: ProfileHolder


, init: function(){
    this.calTags = ko.observableArray();
    this.calTypeOrder = ["you", "twitter people", "popular people", "popular tags"]
    this.loading = ko.observable(false)
    this.populate()
  }

, sorter: function(x, y){
    if(x.selected() && !y.selected()) return -1
    if(x.selected() && y.selected()) return 1
    if(x.cal > y.cal) return 1
    if(x.cal < y.cal) return -1
    return 0
  }

, populate: function(){
    var self = this
    var args = modelPageView.objects.docInfo.calType
    $.get("/f/get_cal_tags", args, function(data){
      console.log("loading profile holder...")
      if(data === 1){
        alert("something wrong happened, please refresh the page and try again")
      }
      else{
        // should be temporary....
        data = ko.utils.arrayFilter(data, function(x){ return x.tag || x.user })
        self.processCalTags(data)
        self.loading(true)
      }
    })
  }

, processCalTags: function(rawData){
    var self = this
    var calTagArray = ko.utils.arrayMap(rawData, function(x){ return new SelectableCalTag(x) })
    var calTags = []


    for(var i in self.calTypeOrder){
      var calType = self.calTypeOrder[i]
      var filteredByCalType = ko.utils.arrayFilter(calTagArray, function(x){
        return x.calType === calType
      })

      filteredByCalType.sort(self.sorter)
      calTags = calTags.concat(filteredByCalType)
    }

    this.calTags(calTags)
  }

, getParentCalTag: function(child, possible){
      if(child.type > possible.type){
        if(child.calType === possible.calType){
          if(possible.type !== 1 ){
            return true;
          }

          if(possible.type === 1 && child.type === 3){
            return possible.cal === child.cal;
          }
        }
      }

      return false;
}


, getSubTypes:  function(calTag, oneLayer){
      var self = this
      return ko.utils.arrayFilter(self.calTags(), function(x){ return calTag.isChild(x, oneLayer);});
  }

, getParentTypes: function(calTag){
      var self = this
      return ko.utils.arrayFilter(self.calTags(), function(x){ return self.getParentCalTag(calTag, x) && x.selected()});
  }

, removeChildren: function(calTag){
      ko.utils.arrayForEach(self.calTags(), function(x){ if(calTag.isChild(x) && x.selected()) removeCal(x) });
}

, removeCal: function(calTag){
      $.post("/f/remove_calendar", calTag.toJSON(), function(data){
          if(data === 1){
            alert("please refresh the page and try again");
          }
          else{
             calTag.select(false);
          }
      });
  }


, removeAll: function(calType){
    var self = this;
    ko.utils.arrayForEach(self.calTags(), function(x){ if(x.calType === calType && x.selected()) self.removeCal(x) });
  }

, selectAll: function(calType){
    var self = this;
    ko.utils.arrayForEach(self.calTags(), function(x){ if(x.calType === calType && !x.selected()) self.addCalendar(x) });
  }

, getChildOfType: function(calType){
      var self = this
      return ko.utils.arrayFilter(self.calTags(), function(x){ return x.calType === calType})
}

, getChunksOfType: function(calType){
      var self = this
      var filtered = ko.utils.arrayFilter(self.calTags(), function(x){ return x.calType === calType && x.type !== 0})
      var result = []
      var i,j,temparray,chunk = 4;
      for (i=0,j=filtered.length; i<j; i+=chunk) {
          result.push(filtered.slice(i,i+chunk));
      }

      return result
}

, clickCalendar: function(calTag){
    calTag.selected() ? this.removeCal(calTag) : this.addCalendar(calTag)
}

, addCalendar: function(calTag){
      var self = this
      $.post("/f/add_calendar", calTag.toJSON(), function(data){
          if(data === 1){
            alert("please refresh the page and try again");
          }
          else{
           var parents = ko.utils.arrayFilter(self.getParentTypes(calTag), function(x){return x.selected()});
           var children = ko.utils.arrayFilter(self.getSubTypes(calTag), function(x){return x.selected()});


         if(parents.length || children.length){
           var for_removal = parents.concat(children);
           console.log("for removal " + JSON.stringify(for_removal))
           ko.utils.arrayForEach(for_removal, function(toRemove){
           self.removeCal(toRemove);
           });
         }

           calTag.selected(true);
          }
      });
    }
}

  modelPageView.ProfileHolder = ProfileHolder

}(modelPageView)

// write unit tests of the above
// we still need to check select deselect logic over
