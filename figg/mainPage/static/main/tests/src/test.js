var expect = chai.expect;

describe('app', function(){
  it('app exists', function(){
    expect(modelPageView).to.be.ok;
  });

  it('event holder exists', function(){
    expect(modelPageView.objects.eventHolder).to.be.ok
  });
  it('event editor factory exists', function(){
    expect(modelPageView.eventEditor).to.be.ok
  });

/*
  it('cal holder exists', function(){
    expect(modelPageView.calHolder).to.be.ok
  });
*/
  it('calTag Factory exists', function(){
    expect(modelPageView.CalTag).to.be.ok
  });

  it('SelectableCalTagFactory exists', function(){
    expect(modelPageView.calHolder.selectableCalTagFactory).to.be.ok
  });

});

/*

describe('event load 1 event from 1 user, then another event from another', function(){
  it('app loaded successful', function(){
    expect(modelPageView.objects.eventHolder.events()).to.have.length(1);
  });

  it('add figg as a calendar', function(){
    var calTag = modelPageViewtcalHolder.selectableCalTagFactory(getFiggCalTag());
    var holder = modelPageView.objects.eventHolder;
    holder.getEventsForCalTag(calTag, holder);
    expect(holder.events()).to.have.length(2);

  });

  it('remove figg as a calendar', function(){
    var calTag = modelPageView.calHolder.selectableCalTagFactory(getFiggCalTag());
    var holder = modelPageView.objects.eventHolder;
    console.log("starting to remove events")
    holder.removeEvents(calTag, holder);
    console.log("finishing removing events")
    expect(holder.events()).to.have.length(1);
  });
});

describe('start with nothing add an event, test date is added', function(){
  it('add an event from 0', function(){
  var holder = modelPageView.objects.eventHolder;
  holder.removeAll();
  var sampleEvent1 = getSampleEvent();
  holder.addEvents([sampleEvent1], holder);
  expect(holder.events()).to.have.length(2);
  });

  it('add another event', function(){
  var sampleEvent2 = getSampleEvent2();
  var holder = modelPageView.objects.eventHolder;
  holder.addEvents([sampleEvent2], holder);
  expect(holder.events()).to.have.length(4);
  });

  it('remove last event', function(){
  var calTag = modelPageView.calHolder.selectableCalTagFactory(getFredKinghamCalTag());
  var holder = modelPageView.objects.eventHolder;
  holder.removeEvents(calTag, holder);
  expect(holder.events()).to.have.length(2);
  expect(_.keys(holder.dates)).to.have.length(1);
  });
});

describe('adding events which have the same user from but different cal types', function(){

  it('should start with nothing', function(){
  var holder = modelPageView.objects.eventHolder;
  holder.removeAll();
  expect(holder.events()).to.have.length(0)
  });

  it('should be able to take 2 events with the same cal tag cal but different types', function(){
    var holder = modelPageView.objects.eventHolder;
    var sampleEvent1 = getSampleEvent();
    var sampleEvent2 = getSampleEvent();
    holder.addEvents([sampleEvent1], holder);
    holder.addEvents([sampleEvent2], holder);
    expect(holder.events()).to.have.length(2);
    expect(_.keys(holder.dates)).to.have.length(1);
    var events = ko.utils.arrayFilter(holder.events(), function(x){ return x.templateName === "eventTmp" });
    expect(events).to.have.length(1);
    var event = events[0];
    expect(event.from()).to.have.length(1);
    expect(event.cal_details).to.have.length(2);
  });

  it('should be able to handle an event with 2 different cals of the same user', function(){
    var holder = modelPageView.objects.eventHolder;
    holder.removeAll();
    holder.addEvents([getSampleEvent3()], holder);
    expect(holder.events()).to.have.length(2);
    var events = ko.utils.arrayFilter(holder.events(), function(x){ return x.templateName === "eventTmp" });
    var event = events[0];
    console.log("event from " + JSON.stringify(event.from()));
    expect(event.from()).to.have.length(1);
    expect(event.cal_details).to.have.length(2);

  });
});

describe('create timeline', function(){
    it('the dateline should be populated', function(){
    expect(modelPageView.objects.dateLineManager).to.be.ok;
    });

});
*/

