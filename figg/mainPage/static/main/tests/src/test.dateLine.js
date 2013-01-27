var expect = chai.expect

var fakeGet = function(func){
  $.get = func
}

var fakePost = function(func){
  $.post = func
}

var FakeStreamHolder = function(){
    this.refresh = function(){}
}

describe('test date', function(){
  it('should get previous', function(){
    var forDate = new Date(2012, 9, 19)
    var monday = forDate.getPreviousDay(1)
    var answer = new Date(2012, 9, 15)
    var result = monday.sameDate(answer)
    expect(result).to.equal(0)
  })

  it('should get the same if the date is already a monday', function(){
    var forDate = new Date(2012, 9, 29)
    var monday = forDate.getPreviousDay(1)
    var result = monday.sameDate(forDate)
    expect(result).to.equal(0)
  })
})


  /*
describe('test that for a month is correct', function(){

  before(function(){
    var forDate = new Date(2012, 9, 19)
    modelPageView.objects.docInfo.today(forDate)
  })

    it('should have 30 dates on a large screen', function(){
    modelPageView.objects.docInfo.size = "large"
    forDate = new Date(2012, 9, 19)
    modelPageView.objects.docInfo.today(forDate)
    modelPageView.objects.dateLineManager = ko.observable()
    modelPageView.objects.dateLineManager(new modelPageView.DateLineManager(forDate))
    modelPageView.objects.streamHolder = new ko.observable(new FakeStreamHolder())
    var dateLineManager = modelPageView.objects.dateLineManager()
    expect(dateLineManager.dates).to.have.length(31)


    expect(dateLineManager.dates[0].date.getMonth()).to.equal(9)
    console.log(dateLineManager.dates[0].date)
    modelPageView.objects.dateLineManager().goBack()
    dateLineManager = modelPageView.objects.dateLineManager()
    var dates = dateLineManager.dates
    expect(dates[0].date.getMonth()).to.equal(8)
    expect(dates[dates.length - 1].date.getMonth()).to.equal(8)
    expect(dateLineManager.dates).to.have.length(30)
    })


    it('should just a month forward easily', function(){
      var dateLineManager, dates, min, max
      modelPageView.objects.docInfo.size = "large"
      forDate = new Date(2012, 9, 19)
      modelPageView.objects.docInfo.today(forDate)
      modelPageView.objects.dateLineManager = ko.observable()
      modelPageView.objects.dateLineManager(new modelPageView.DateLineManager(forDate))
      modelPageView.objects.streamHolder = new ko.observable(new FakeStreamHolder())
      modelPageView.objects.dateLineManager().goForward()

      dateLineManager = modelPageView.objects.dateLineManager()
      expect(dateLineManager.dates).to.have.length(30)
      dates = dateLineManager.dates
      min = dates[0]
      expect(min.date.getDay(), 1)
      expect(min.date.getDate()).to.equal(1)
      expect(min.date.getMonth()).to.equal(10)
      max = dates[dates.length - 1]
      expect(max.date.getMonth()).to.equal(10)
      expect(max.date.getDate()).to.equal(30)
    })

    it('should have 14 dates on a medium screen', function(){
      forDate = new Date(2012, 9, 19)
      var dateLineManager, dates, min, max
      modelPageView.objects.docInfo.size = "medium"
      modelPageView.objects.docInfo.today(forDate)
      modelPageView.objects.dateLineManager = ko.observable()
      modelPageView.objects.dateLineManager(new modelPageView.DateLineManager(forDate))
      modelPageView.objects.streamHolder = new ko.observable(new FakeStreamHolder())
      dateLineManager = modelPageView.objects.dateLineManager()
      dates = dateLineManager.dates
      expect(dateLineManager.rangeType).to.equal(1)
      expect(dateLineManager.dates).to.have.length(14)
      dates = dateLineManager.dates
      min = dates[0]
      expect(min.date.getDay(), 1)
      expect(min.date.getDate()).to.equal(15)
      expect(min.date.getMonth()).to.equal(9)
      max = dates[dates.length - 1]
      expect(max.date.getMonth()).to.equal(9)
      expect(max.date.getDate()).to.equal(28)


      modelPageView.objects.dateLineManager().goBack()
      
      dateLineManager = modelPageView.objects.dateLineManager()
      expect(dateLineManager.dates).to.have.length(14)
      dates = dateLineManager.dates
      min = dates[0]
      max = dates[dates.length - 1]
      console.log("min date " + min.date)
      console.log("max date " + max.date)
      expect(min.date.getDate()).to.equal(1)
      expect(min.date.getMonth()).to.equal(9)
      expect(min.date.getDay(), 1)
      expect(max.date.getMonth()).to.equal(9)
      expect(max.date.getDate()).to.equal(14)
      expect(min.date.getDay(), 6)
    })

    it('should just a fortnight forward easily', function(){
      var dateLineManager, dates, min, max
      modelPageView.objects.docInfo.size = "medium"
      forDate = new Date(2012, 9, 19)
      modelPageView.objects.docInfo.today(forDate)
      modelPageView.objects.dateLineManager = ko.observable()
      modelPageView.objects.dateLineManager(new modelPageView.DateLineManager(forDate))
      modelPageView.objects.streamHolder = new ko.observable(new FakeStreamHolder())
      modelPageView.objects.dateLineManager().goForward()

      dateLineManager = modelPageView.objects.dateLineManager()
      expect(dateLineManager.dates).to.have.length(14)
      dates = dateLineManager.dates
      min = dates[0]
      expect(min.date.getDay(), 1)
      expect(min.date.getDate()).to.equal(29)
      expect(min.date.getMonth()).to.equal(9)
      max = dates[dates.length - 1]
      expect(max.date.getMonth()).to.equal(10)
      expect(max.date.getDate()).to.equal(11)
    })


    it('should have 7 dates on a small screen', function(){
    forDate = new Date(2012, 9, 19)
    var dateLineManager, dates, min, max
    modelPageView.objects.docInfo.size = "small"
    modelPageView.objects.docInfo.today(forDate)
    modelPageView.objects.dateLineManager = ko.observable()
    modelPageView.objects.dateLineManager(new modelPageView.DateLineManager(forDate))
    modelPageView.objects.streamHolder = new ko.observable(new FakeStreamHolder())
    dateLineManager = modelPageView.objects.dateLineManager()
    dates = dateLineManager.dates
    expect(dateLineManager.rangeType).to.equal(2)
    expect(dateLineManager.dates).to.have.length(7)
    dates = dateLineManager.dates
    min = dates[0]
    expect(min.date.getDay(), 1)
    expect(min.date.getDate()).to.equal(15)
    expect(min.date.getMonth()).to.equal(9)
    max = dates[dates.length - 1]
    expect(max.date.getMonth()).to.equal(9)
    expect(max.date.getDate()).to.equal(21)
    expect(max.date.getDay(), 6)


    modelPageView.objects.dateLineManager().goBack()
    
    dateLineManager = modelPageView.objects.dateLineManager()
    expect(dateLineManager.dates).to.have.length(7)
    dates = dateLineManager.dates
    min = dates[0]
    max = dates[dates.length - 1]
    expect(min.date.getDate()).to.equal(8)
    expect(min.date.getMonth()).to.equal(9)
    expect(min.date.getDay(), 1)
    expect(max.date.getMonth()).to.equal(9)
    expect(max.date.getDate()).to.equal(14)
    expect(min.date.getDay(), 6)
    })

    it('should just a fortnight forward easily', function(){
      var dateLineManager, dates, min, max
      modelPageView.objects.docInfo.size = "small"
      forDate = new Date(2012, 9, 19)
      modelPageView.objects.docInfo.today(forDate)
      modelPageView.objects.dateLineManager = ko.observable()
      modelPageView.objects.dateLineManager(new modelPageView.DateLineManager(forDate))
      modelPageView.objects.streamHolder = new ko.observable(new FakeStreamHolder())
      modelPageView.objects.dateLineManager().goForward()

      dateLineManager = modelPageView.objects.dateLineManager()
      expect(dateLineManager.dates).to.have.length(7)
      dates = dateLineManager.dates
      min = dates[0]
      expect(min.date.getDay(), 1)
      expect(min.date.getDate()).to.equal(22)
      expect(min.date.getMonth()).to.equal(9)
      max = dates[dates.length - 1]
      expect(max.date.getMonth()).to.equal(9)
      expect(max.date.getDate()).to.equal(28)
    })

})
    */
