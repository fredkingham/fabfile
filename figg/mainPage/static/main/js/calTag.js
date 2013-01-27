!function(modelPageView){
  "use strict"

var CalTag = function( calTag ){
  this.init(calTag)
}


CalTag.prototype = {
  constructor: CalTag

, init: function( calTag ){
    this.calType = calTag.cal_type;
    this.cal = calTag.user ? calTag.user : undefined;
    this.tag = calTag.tag ? calTag.tag : undefined;
    this.type = this.getType();
    this.img = calTag.img
}

, className: "CalTag"

, equals: function(x){
      return (x.calType === this.calType) && (x.cal === this.cal) && (x.tag === this.tag);
  }

, sameCal: function(x){
      return x.cal === this.cal;
}

, isChild: function(possible, oneLayer){

      if(this.type < possible.type){
        if(this.calType === possible.calType){

            if(oneLayer){
              return this.type === 0 && (possible.type === 1 || possible.type === 2);
            }
            else{
            return true;
            }
          }

          if(this.type === 1 && possible.type === 3){
            return possible.cal === this.cal;
          }
        }
        return false;
      }

, getType: function(){
    if(this.tag && this.cal){
      return 3;
    }

    return this.tag ? 2 : this.cal ? 1 : 0
  }


, onlyTag: function(){
      return this.type === 2;
  }  

, isRelated: function(calTag){
      return this.equals(calTag) || calTag.isChild(this) || this.isChild(calTag)
}

, toJSON: function(){
      return {"cal": this.cal, "tag": this.tag, "calType": this.calType}  }
}

modelPageView.CalTag = CalTag

}(modelPageView);



