"use strict"

var expect = chai.expect

var fakeGet = function(func){
  $.get = func
}

var fakePost = function(func){
  $.post = func
}

// defaults
$.get = function(url, args, callback){
    if(!url){
      throw "url required"
    }


}

/*


describe('single cal profileHolder', function(){

  before(function(){
  fakeGet(function(url, args, func){
      if(url != '/!get_cal_tags') throw "wrong url"
          func([{
          cal_type: "twitter people",
          img: "F_i_g_g/mini/for-twitter_mini.png",
          revealed: false,
          selected: false,
          tag: null,
          user: "F_i_g_g"
      }])
  })
  modelPageView.objects.streamHolder = new modelPageView.ProfileHolder()
  })

  it('model page view exists', function(){
    expect(modelPageView).to.be.ok
    expect(modelPageView.objects.streamHolder).to.be.ok
    expect(modelPageView.objects.streamHolder.calTags()).to.have.length(1)
    var calTag = modelPageView.objects.streamHolder.calTags()[0]
    expect(calTag.selected()).to.be.false
  })
})

describe('double cal profileHolder', function(){

  before(function(){
    fakeGet(function(url, args, func){
           var calTag1 = {
              cal_type: "twitter people",
              img: undefined,
              revealed: false,
              selected: false,
              tag: undefined,
              user: "F_i_g_g"
           }

           var calTag2 = {
              cal_type: "twitter people",
              img: undefined,
              revealed: false,
              selected: true,
              tag: undefined,
              user: "fredkingham"
           }
       func([ calTag1, calTag2 ])
       })

      modelPageView.objects.streamHolder.populate()
  })


  it('it should load populate', function(){
      expect(modelPageView.objects.streamHolder.calTags()).to.have.length(2)
    })

  it('it should have the parent selected', function(){
      var calTags = modelPageView.objects.streamHolder.calTags()
      var selectedCalTags = ko.utils.arrayFilter(calTags, function(x){
        return x.selected()
      })

      expect(selectedCalTags).to.have.length(1)
      var selected = selectedCalTags[0]
      console.log("selected is " + JSON.stringify(selected))
      expect(selected.cal).to.equal("fredkingham")
      expect(selected.tag).to.be.undefined

      var notSelectedCalTags = ko.utils.arrayFilter(calTags, function(x){
        return !x.selected()
      })

      expect(notSelectedCalTags).to.have.length(1)
      var notSelected = notSelectedCalTags[0]
      expect(notSelected.cal).to.equal("F_i_g_g")
      expect(notSelected.tag).to.be.undefined
  })

  it('if we remove one then both should not be selected', function(){

      fakePost(function(url, args, func){
        if(url !== "/!remove_calendar") throw "wrong address"
        func(0)
      })

      var calTags = modelPageView.objects.streamHolder.calTags()

      var selectedCalTags = ko.utils.arrayFilter(calTags, function(x){
        return x.selected()
      })

      for(var i in selectedCalTags){
        var selectedCalTag = selectedCalTags[i]
        console.log("hey " + selectedCalTag.selected())
      }

      expect(selectedCalTags).to.have.length(1)
      modelPageView.objects.streamHolder.clickCalendar(selectedCalTags[0])

      var calTags = modelPageView.objects.streamHolder.calTags()
      var notSelectedCalTags = ko.utils.arrayFilter(calTags, function(x){
        return !x.selected()
      })

      expect(notSelectedCalTags).to.have.length(2)
  })


}) 



*/



