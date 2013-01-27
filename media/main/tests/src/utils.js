

function getSampleEvent(){

return {
  attending_status: [6, 0],
  cal_details: [['you', 'fredkingham', null]],
  cancelled: false,
  date: "2012-08-28",
  description: false,
  from: [{
          cal_type: "you",
          img: "fredkingham/mini/left_mini.png",
          revealed: false,
          selected: false,
          tag: null,
          user: "fredkingham"
        }],
  id: 1,
  img: "fredkingham/normal/left_normal.png",
  noteCount: 0,
  public: 0,
  time: false,
  time_name: "None",
  title: "something tomorrow",
  venue: false
  }
}

function getSampleEvent2(){
  var sample = getSampleEvent();
  sample.cal_details = [['twitter people', 'F_i_g_g', null]];
  sample.date = "2012-08-27";
  sample.id = 2;
  sample.from = [{
    cal_type: "twitter people",
    img: "F_i_g_g/mini/for-twitter_mini.png",
    revealed: false,
    selected: false,
    tag: null,
    user: "F_i_g_g"
  }];

  return sample
}

function getSampleEvent3(){
  var sample = getSampleEvent();
  sample.cal_details = [['twitter people', 'Dave', null]];
  sample.date = "2012-08-27";
  sample.id = 3;
  sample.from = [{
    cal_type: "twitter people",
    img: "F_i_g_g/mini/for-twitter_mini.png",
    revealed: false,
    selected: false,
    tag: null,
    user: "F_i_g_g"
  },
  {
    cal_type: "popular people",
    img: "F_i_g_g/mini/for-twitter_mini.png",
    revealed: false,
    selected: false,
    tag: null,
    user: "F_i_g_g"
    }
  ];

  return sample
}

function getFiggCalTag(){
  return {
        cal_type: "twitter people",
        img: "F_i_g_g/mini/for-twitter_mini.png",
        revealed: false,
        selected: false,
        tag: null,
        user: "F_i_g_g"
    };
}

function getFredKinghamCalTag(){
  return {
          cal_type: "you",
          img: "fredkingham/mini/left_mini.png",
          revealed: false,
          selected: false,
          tag: null,
          user: "fredkingham"
    };
}


$.get = function(url, args, callBack){
  if(url === "/!get_all_events"){
      var data = [getSampleEvent()]
      var result = {}
      result.more = true;
      result.events = data
      callBack(result);
  }

}

$.post = function(url, args, callBack){

  if(url ==="/!get_cal_json"){
      var data = [getSampleEvent2()]
      var result = {}
      result.events = data
      result.more = true
      callBack(result);
  }

}




