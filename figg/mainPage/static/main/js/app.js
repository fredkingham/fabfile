$(document).ajaxSend(function (event, xhr, settings) {

    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) == (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    function sameOrigin(url) {
        // url could be relative or scheme relative or absolute
        var host = document.location.host; // host + port
        var protocol = document.location.protocol;
        var sr_origin = '//' + host;
        var origin = protocol + sr_origin;
        // Allow absolute or scheme relative URLs to same origin
        return (url == origin || url.slice(0, origin.length + 1) == origin + '/') ||
            (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') ||
            // or any other URL that isn't scheme relative or absolute i.e relative.
            !(/^(\/\/|http:|https:).*/.test(url));
    }
    function safeMethod(method) {
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }

    if (!safeMethod(settings.type) && sameOrigin(settings.url)) {
        xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
    }
});


var createDate = function(someDate){
  var result = new Date(someDate)

  if(!result.getTime || isNaN(result.getTime())){
    var arr = someDate.split(/[- :]/)
    if(arr.length == 3){
      result = new Date(arr[0], arr[1]-1, arr[2]);
    }
    else{
      result = new Date(arr[0], arr[1]-1, arr[2], arr[3], arr[4], arr[5]);
    }
  }

  if(!result.getTime || isNaN(result.getTime())){
      if(someDate.length === 8){
        var year = someDate.substring(0, 4)
        var month = someDate.substring(4, 6)
        var day = someDate.substring(6, 8)
        result = new Date(parseInt(year, 10), parseInt(month, 10) -1, parseInt(day, 10))
      }
  }

  return result
}


Date.prototype.getMonthName = function() {
var m = ['January','February','March','April','May','June','July',
'August','September','October','November','December'];
return m[this.getMonth()];
}

Date.prototype.getShortMonthName = function(){
var m = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug',
  'Sep', 'Oct', 'Nov', 'Dec'];
return m[this.getMonth()];
}

Date.prototype.getShortDayName = function(){
  var d = ['Sun','Mon','Tue','Wed',
  'Thur','Fri','Sat'];
  return d[this.getDay()];
}

/*
 * takes in the indices of a date type returns a new date of the previous
 * date type
 */
Date.prototype.getPreviousDay = function(x){
  var delta = x - this.getDay()
  var monday = new Date(this.getFullYear(), this.getMonth(), this.getDate() + delta)

  return monday
}

Date.prototype.getDayName = function() {
var d = ['Sunday','Monday','Tuesday','Wednesday',
'Thursday','Friday','Saturday'];
return d[this.getDay()];
}

Date.prototype.displayName = function(){
  return this.getShortDayName() + ", " + String(this.getDate()) + " " + this.getShortMonthName()
}

Date.prototype.asLink = function(){
  return String(this.getFullYear()) + "/" + this.justified(this.getMonth() + 1) + "/" + this.justified(this.getDate())
}

// returns -1 if less than, 0 if the same as, or 1 if greater than
Date.prototype.sameDate = function(otherDate){
    var ourDate = new Date(this)
    ourDate.setHours(0, 0, 0, 0); 
    var ourTime = ourDate.getTime();
    var theirDate = new Date(otherDate)
    theirDate.setHours(0, 0, 0, 0);
    var theirTime = theirDate.getTime();

    return ourTime == theirTime ? 0 : ourTime < theirTime ? -1 : 1; 
  }

Date.prototype.equalDate = function(otherDate){
    return this.sameDate(otherDate) === 0
  }

Date.prototype.isTomorrow = function(otherDate){
    var possibleTomorrow = new Date(this).setDate( this.getDate() + 1 );
    return otherDate.sameDate(possibleTomorrow);
}

Date.prototype.asInt = function(){
    return parseInt(String(this.getFullYear()) + this.justified(this.getMonth() + 1) + this.justified(this.getDate()), 10)
}

Date.prototype.justified = function(someInt){
  var someString = String(someInt);
  if(someString.length === 1) someString = "0" + someString
  return someString
}

ko.bindingHandlers.slideVisible = {
    init: function(element, valueAccessor){
        $(element).toggle(ko.utils.unwrapObservable(valueAccessor()));
    }
    , update: function(element, valueAccessor){
        var val = ko.utils.unwrapObservable(valueAccessor());
        
        if(val){
           $(element).slideDown(ko.bindingHandlers.slideVisible.duration);   
        }
        else{
          if($(element).is(":visible")){
             $(element).slideUp(ko.bindingHandlers.slideVisible.duration);   
           }
        }
      }

    , duration: 100        
};

ko.bindingHandlers.hoverToggle = {
    update: function(element, valueAccessor) {
       var css = valueAccessor();

        ko.utils.registerEventHandler(element, "mouseover", function() {
            ko.utils.toggleDomNodeCssClass(element, ko.utils.unwrapObservable(css), true);
        });  

        ko.utils.registerEventHandler(element, "mouseout", function() {
            ko.utils.toggleDomNodeCssClass(element, ko.utils.unwrapObservable(css), false);
        });      
    } 
};

ko.bindingHandlers.modal = {
    init: function(element, valueAccessor, allBindingsAccessor) {
        var allBindings = allBindingsAccessor();
        var $element = $(element);
        $element.addClass('hide modal');

        if (allBindings.modalOptions) {
            if (allBindings.modalOptions.beforeClose) {
                $element.on('hide', function() {
                    return allBindings.modalOptions.beforeClose();
                });
            }
        }

        return ko.bindingHandlers['with'].init.apply(this, arguments);
    },
    update: function(element, valueAccessor) {
        var value = ko.utils.unwrapObservable(valueAccessor());

        var returnValue = ko.bindingHandlers['with'].update.apply(this, arguments);

        if (value) {
            $(element).modal('show');
        } else {
            $(element).modal('hide');
        }

        return returnValue;
    }
};


ko.bindingHandlers.fileAdded = {

update: function(element, valueAccessor, allBindingsAccessor){
      var value = valueAccessor()
      var allBindings = allBindingsAccessor()
      var func = allBindings.previewFunc
      if(element.files.length && value){
          func(element.files)
      }
  }
}


ko.bindingHandlers.filePreview = {
  update: function(element, valueAccessor, allBindingsAccessor){
      var allBindings = allBindingsAccessor()
      if(!!FileReader && valueAccessor() && element.files.length){
        var reader = new FileReader();
        reader.onload = function(event){
          var dataUri = event.target.result
          allBindings.imagePreview(dataUri)
        }
        reader.onerror = function(e) {
          console.log("error", stuff)
        }
        reader.readAsDataURL(element.files[0])
    }
  }
}

ko.bindingHandlers.tooltip = {
    init: function(element, valueAccessor){
        $(element).tooltip({placement: "bottom", title: ko.utils.unwrapObservable(valueAccessor())});
    }
}

ko.bindingHandlers.datepicker = {
    init: function(element, valueAccessor, allBindingsAccessor) {
        //initialize datepicker with some optional options
        var options = allBindingsAccessor().datepickerOptions || {};

        $(element).datepicker(options);

        //handle the field changing
        ko.utils.registerEventHandler(element, "change", function() {
            var observable = valueAccessor();
            observable(new Date($(element).datepicker("getDate")));
        });

        //handle disposal (if KO removes by the template binding)
        ko.utils.domNodeDisposal.addDisposeCallback(element, function() {
            $(element).datepicker("destroy");
        });

    },
    update: function(element, valueAccessor) {
        var value = ko.utils.unwrapObservable(valueAccessor()),
            current = $(element).datepicker("getDate");
        
        if (value - current !== 0) {
            $(element).datepicker("setDate", value);   
        }
    }
};

ko.bindingHandlers.scrollBottom = {

  updating: true,

  init: function(element, valueAccessor, allBindingsAccessor) {
      var self = this
      self.updating = true;
      ko.utils.domNodeDisposal.addDisposeCallback(element, function() {
            $(window).off("scroll.ko.scrollBottomHandler")
            self.updating = false
      });
  },

  update: function(element, valueAccessor, allBindingsAccessor){
    var props = allBindingsAccessor().scrollOptions
    var offset = props.height ? props.height : "0"
    var loadFunc = props.loadFunc
    var load = ko.utils.unwrapObservable(valueAccessor());
    var self = this;

    if(load){
      element.style.display = "";
      $(window).on("scroll.ko.scrollBottomHandler", function(){
        if(($(document).height() - offset <= $(window).height() + $(window).scrollTop())){
          if(self.updating){
            loadFunc()
            self.updating = false;
          }
        }
        else{
          self.updating = true;
        }
      });
    }
    else{
        element.style.display = "none";
        $(window).off("scroll.ko.scrollBottomHandler")
        self.updating = false
    }
  }
}

ko.bindingHandlers.startDown =  {
  update: function(element, valueAccessor){
    var load = ko.utils.unwrapObservable(valueAccessor());
    if(load){
      $(window).scrollTop(150)
    }
  }
}

ko.bindingHandlers.scrollTop = {

  updating: false,

  blah: "something",

  init: function(element, valueAccessor, allBindingsAccessor) {
      ko.utils.domNodeDisposal.addDisposeCallback(element, function() {
            $(window).off("scroll.ko.scrollTopHandler")
      });
  },

  update: function(element, valueAccessor, allBindingsAccessor){
    var props = allBindingsAccessor().scrollOptions
    var loadFunc = props.loadFunc
    var load = ko.utils.unwrapObservable(valueAccessor());
    var self = this;
    $(window).off("scroll.ko.scrollTopHandler")


    if(load){
      element.style.display = "";
        $(window).on("scroll.ko.scrollTopHandler", function(){
          if($(window).scrollTop() < 150){
              loadFunc()
            }
        });
    }
    else{
        $(window).off("scroll.ko.scrollTopHandler")
        element.style.display = "none";
        self.updating = false
    }
  }
}

ko.bindingHandlers.jqAuto = {
    init: function (element, valueAccessor, allBindingsAccessor, viewModel) {
        var options = valueAccessor() || {},
        allBindings = allBindingsAccessor(),
        unwrap = ko.utils.unwrapObservable,
        modelValue = allBindings.jqAutoValue,
        labelValue = allBindings.jqLabelValue,
        source = allBindings.jqAutoSource,
        query = allBindings.jqAutoQuery,
        valueProp = allBindings.jqAutoSourceValue,
        inputValueProp = allBindings.jqAutoSourceInputValue || valueProp,
        labelProp = allBindings.jqAutoSourceLabel || inputValueProp;
        funcProp = allBindings.jqFuncProp

        //function that is shared by both select and change event handlers 
        function writeValueToModel(valueToWrite, labelToWrite) {
            if (ko.isWriteableObservable(modelValue)) {
                modelValue(valueToWrite);
                labelValue(labelToWrite)
            } else {  //write to non-observable 
                if (allBindings['_ko_property_writers'] && allBindings['_ko_property_writers']['jqAutoValue'])
                    allBindings['_ko_property_writers']['jqAutoValue'](valueToWrite);
            }
        }

        //on a selection write the proper value to the model 
        options.select = function (event, ui) {
            if(ui.item && ui.item.func){
                ui.item.func();
                return;
            }

            var actVal = ui.item ? ui.item.actualValue : null
            var labelVal = ui.item ? ui.item.label : null
            

            writeValueToModel(actVal, labelVal);
        };

        //on a change, make sure that it is a valid value or clear out the model value 
        options.change = function (event, ui) {
            var currentValue = $(element).val();
            var matchingItem = ko.utils.arrayFirst(unwrap(source), function (item) {
                return unwrap(inputValueProp ? item[inputValueProp] : item) === currentValue;
            });

            if (!matchingItem) {
                writeValueToModel(currentValue);
            }
        };

        //hold the autocomplete current response 
        var currentResponse = null;

        //handle the choices being updated in mappedSource, to decouple value updates from source (options) updates 
        var mappedSource = ko.computed({
            read: function () {
                mapped = ko.utils.arrayMap(unwrap(source), function (item) {
                    var result = {};
                    result.label = labelProp ? unwrap(item[labelProp]) : unwrap(item).toString();  //show in pop-up choices 
                    result.value = inputValueProp ? unwrap(item[inputValueProp]) : unwrap(item).toString();  //show in input box 
                    result.actualValue = valueProp ? unwrap(item[valueProp]) : item;  //store in model 
                    result.func = funcProp ? unwrap(item[funcProp]) : null;
                    return result;
                });
                return mapped;
            },
            write: function (newValue) {
                source(newValue);  //update the source observableArray, so our mapped value (above) is correct 
                if (currentResponse) {
                    currentResponse(mappedSource());
                }
            },
            disposeWhenNodeIsRemoved: element
        });

        if (query) {
            options.source = function (request, response) {
                currentResponse = response;
                query.call(this, request.term, mappedSource);
            };
        } else {
            //whenever the items that make up the source are updated, make sure that autocomplete knows it 
            mappedSource.subscribe(function (newValue) {
                $(element).autocomplete("option", "source", newValue);
            });

            options.source = mappedSource();
        }


        //initialize autocomplete 
        $(element).autocomplete(options);
    },
    update: function (element, valueAccessor, allBindingsAccessor, viewModel) {
        //update value based on a model change 
        var allBindings = allBindingsAccessor(),
        unwrap = ko.utils.unwrapObservable,
        modelValue = unwrap(allBindings.jqAutoValue) || '',
        valueProp = allBindings.jqAutoSourceValue,
        inputValueProp = allBindings.jqAutoSourceInputValue || valueProp;

        //if we are writing a different property to the input than we are writing to the model, then locate the object 
        if (valueProp && inputValueProp !== valueProp) {
            var source = unwrap(allBindings.jqAutoSource) || [];
            var modelValue = ko.utils.arrayFirst(source, function (item) {
                return unwrap(item[valueProp]) === modelValue;
            }) || {};
        }

        //update the element with the value that should be shown in the input 
        var newValue = (modelValue && inputValueProp !== valueProp) ? unwrap(modelValue[inputValueProp]) : modelValue.toString();
        if (newValue || newValue === 0) {
            $(element).val(newValue);
        }
    }
};

var modelPageView = function(){
  "use strict"
  "initialise the modal"

function MainPageViewModal(){

var self = this;
var updated = false;
self.updates = ko.observableArray([]);
self.updated = ko.observable(updated);
self.objects = {}
self.constants = {}
self.decorators = {}
self.utils = {}

this.read = function(){
  if(!updated){
  $.post('/!read_notification/', {}, function(data){
    if(0 === data){
      alert("something wrong happened, please refresh the page");
    }
    else if(data.length){
      if(!updated){
      updated = true;
      for(row in data){
        self.updates.push(new Update(data[row]));
      }
      }
    }
    else{
        if(!updated){
          self.updates.push("No new updates");
          updated = true;
        }
    }
  })
  }
}
}

  return new MainPageViewModal();
}();


!(function(modelPageView){
  "use string"

  modelPageView.utils.enrichText = function(txt){
           var link_pattern = /\b((?:[a-z][\w-]+:(?:\/{1,3}|[a-z0-9%])|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}\/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’]))/i;

           var addWWWIfNec = function(potential){
                if(potential.substring(0, 4) != "http"){
                   return "http://" + potential
                }

                return potential
           }

           var getRegexResults = function(txt, regex){
                var result = []
                var found
                var index = 0
                var count = 0
                while(found = regex.exec(txt.substring(index))){
                if(!found) break;
                result.push(found[1])
                index = found.index + found[1].length
                }
                return result
           }

           var replaceRegex = function(txt, results, post_func){
              for(var i in results){
                    txt.replace(results[i], post_func(results[i]))
              }
           }

           var links = getRegexResults(txt, link_pattern);
           
           ko.utils.arrayForEach(links, function(x){ 
             var link = addWWWIfNec(x)
             var replacement = '<a href="' + link + '">' + x + "</a>"
             txt = txt.replace(x, replacement) 
           })

           var tag_pattern = /#(\w+)/g;
           txt = txt.replace(tag_pattern, '<a href="/t/$1">#$1</a>');
           var at_pattern = /@(\w+)/g;
           txt = txt.replace(at_pattern, '<a href="/$1">@$1</a>');
           return txt;
}

})(modelPageView);

!function(modelPageView){
  "use strict"

var DocInfo = function(){
      var self = this;
      this.today = ko.observable(new Date());
      this.forDate = ko.observable(new Date());
      setInterval(function(){self.today(new Date())},40000);
      this.cal = false;
      this.tag = false;
      this.search = false;
}

modelPageView.objects.docInfo = new DocInfo();

var width = $(window).width()
modelPageView.objects.docInfo.size = width < 840 ? "small" : width > 1220 ? "large" : "medium"
function constructURL(someDate){
    var link = "/";
    if(modelPageView.objects.docInfo.cal) link = link + modelPageView.objects.docInfo.cal + "/"
    if(modelPageView.objects.docInfo.tag) link = link + "t/" + modelPageView.objects.docInfo.tag + "/"
    if(someDate) link = link + "d/" + someDate.asLink()
    return link
}

modelPageView.utils.constructURL = constructURL

function SearchHelper(){
  this.submit = function(formElement){
      window.location.href="/#s/" + document.getElementById("search-query").value
  }

}

modelPageView.objects.searchHelper = new SearchHelper()


function GenericHolder(){
  this.genericInit()
  throw "this is an abstract class and should never be called"
}

GenericHolder.prototype = {
  constructor: GenericHolder

  , genericInit: function(){
    this.loading = ko.observable(true)
    this.populate()
    this.loadingMoreBottom = false
    this.loadingMoreTop = false
    this.updatingTop = ko.observable(false)
    this.updatingBottom = ko.observable(false)
    this.events = ko.observableArray([])
    var self = this;
    this.streamType = ko.observable("events")

    this.updateBottom = function(){
      if(!self.events().length){
          self.updatingBottom(false)
        }
        else{
          self.loadBottom()
        }
      }

    this.updateTop = function(){
      self.loadTop()
    }
  }

  , loadTop: function(){
      throw "this is an abstract class and this should never be reahed"
  }

  , loadBottom: function(){
      throw "this is an abstract class and this should never be reahed"
  }


  , dateChange: function(indexFunc){
      var index = indexFunc()
      if(index === 0) return true

      var events = this.events()
      return events[index].date.sameDate(events[index -1 ].date) !== 0
  }

  , refresh: function(){
      this.updated(false)
      this.events([])
      this.populate()
  }
}

modelPageView.GenericHolder = GenericHolder


}(modelPageView);
