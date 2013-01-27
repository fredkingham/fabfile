/*
 * Copyright 2012 Fred Kingham
 *
 * http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

 /*
 * (derived from the boostrap scroll spy plug in
 * http://twitter.github.com/bootstrap
 */

 !function(modelPageView){
"use strict"

 function DateLineSpy(){
    this.offsets = []
    this.targets = []
    this.refresh()
 }

 DateLineSpy.prototype = {
    constructor: DateLineSpy

,   refresh: function(){
      var self = this
      this.targets = []
      this.offsets = []
      $(".date").each(function(index, value){
        self.offsets.push($(value).position().top)
        var dateId = $(value).attr("id")
        self.targets.push(createDate(dateId.substring(1)))
      })
      this.setup()
}

,   process: function(){
      var scrollTop = $(window).scrollTop() + 400
      , offsets = this.offsets
      , targets = this.targets
      

      // currently will never initialise i
      for( var i = this.offsets.length; i--;){
            if(scrollTop >= offsets[i]){
                if(!offsets[i + 1] || scrollTop <= offsets[i + 1]){
                  if(targets[i] !== modelPageView.objects.dateLineManager().active()){
                    this.activate(targets[i])
                  }
                }
              }
            }
      }


,   activate: function(date){
      modelPageView.objects.dateLineManager().activateDateSection(date)
    }  

,   setup: function(){
       $(window).on('scroll.date-line-spy', function(){
         modelPageView.objects.dateLineSpy.process()
       })
}

,   tearDown: function(){
        $(window).off('scroll.date-line-spy')
    }

}


 modelPageView.objects.dateLineSpy = new DateLineSpy()


 }(modelPageView)
