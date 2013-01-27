describe('Date', function(){
  describe('month names', function(){
    it('it should return the correct date types', function(){
      var date = new Date(2012, 8, 19);
      console.log(date.getShortMonthName());
      assert(date.getShortMonthName() === "Aug");
      assert(date.getMonthName() === "August");

    })
  })
})

describe('ModelPageView', function(){
  describe('DocInfo', function(){
    it('it should have a docinfo that is th correct date', function(){
      assert(modelPageView);
    })
  })
})
