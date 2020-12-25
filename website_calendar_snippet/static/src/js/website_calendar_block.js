odoo.define('website_calendar_snippet.animation', function (require) {
'use strict';



var core = require('web.core');
var base = require('web_editor.base');
var animation = require('website.content.snippets.animation');
var qweb = core.qweb;
var _t = core._t;

animation.registry.s_calendar= animation.Class.extend({

        selector: "section.s_calendar",

        start : function() {
            var self = this;


                var $calendar = self.$target.find('.calendar');
                //var $calendar=self.$target.filter(
                //      function() {
                //          return $(this).hasClass('calendar');
                //        }
                //    );
                $calendar.html('');

                var all_filters = {};
                var color_map = {};

                var get_color = function(key) {
                    if (color_map[key]) {
                        return color_map[key];
                    }
                    var index = (((_.keys(color_map).length + 1) * 5) % 24) + 1;
                    color_map[key] = index;
                    return index;
                }
                    var localeData = moment.localeData();


                    var shortTimeformat = localeData.longDateFormat('LT')+":00";
                    var dateFormat ="d/M/yyyy";
                    //console.log(window.location.protocol + '//' + window.location.hostname);
                    var options={
                        events: function(start, end, callback) {
                            $.ajax({
                                url: '/calendar_block/get_events/' + Math.round(start.getTime() / 1000) + '/' + Math.round(end.getTime() / 1000),
                                dataType: 'json',
                                success: function(result) {
                                    //Setup colors
                                    all_filters[0] = get_color(result.contacts[0]);
                                    all_filters[-1] = get_color(-1);
                                    _.each(result.contacts, function (c) {
                                        if (!all_filters[c] && c != result.contacts[0]) {
                                            all_filters[c] = get_color(c);
                                        }
                                    });

                                    //Mutate data for calendar
                                    var events = result.events;
                                    for(var i = 0; i < events.length; i++) {
                                        events[i].start = Date.parseExact(events[i].start, "yyyy-MM-dd HH:mm:ss");
                                        events[i].end = Date.parseExact(events[i].end, "yyyy-MM-dd HH:mm:ss");
                                        var start_offset = events[i].start.getTimezoneOffset();
                                        var end_offset = events[i].end.getTimezoneOffset();
                                        start_offset = start_offset - (start_offset * 2);
                                        end_offset = end_offset - (end_offset * 2);
                                        events[i].start.addMinutes(start_offset);
                                        events[i].end.addMinutes(end_offset);

                                        for(var j = 0; j < events[i].attendees.length; j++) {
                                            events[i].title += '<img title="' + events[i].attendees[j].name + '" class="attendee_head" src="/web/binary/image?model=res.partner&field=image_small&id=' + events[i].attendees[j].id + '" />';
                                            //if (all_filters[events[i].color] !== undefined) {
                                            events[i].className = 'calendar_color_' + events[i].color; //all_filters[events[i].color];
                                            //}
                                            //else  {
                                            //    events[i].className = 'cal_opacity calendar_color_'+ all_filters[-1];
                                            //}
                                        }
                                    }
                                    callback(events);
                                }
                            });
                        },
                        weekNumberTitle: _t("W"),
                        allDayText: _t('All day'),
                        buttonText : {
                            today: _t("Today"),
                            month: _t("Month"),
                            week: _t("Week"),
                            day: _t("Day")
                        },
                        firstDay: moment.localeData().firstDayOfWeek(),
                        aspectRatio: 1.8,
                        snapMinutes: 15,
                        weekMode : 'liquid',
                        columnFormat: {
                            month: 'ddd',
                            week: 'ddd ' + dateFormat,
                            day: 'dddd ' + dateFormat,
                        },
                        titleFormat: {
                            month: 'MMMM yyyy',
                            week: dateFormat + "{ '&#8212;'"+ dateFormat,
                            day: dateFormat,
                        },
                        timeFormat : {
                           // for agendaWeek and agendaDay
                           agenda: shortTimeformat + '{ - ' + shortTimeformat + '}', // 5:00 - 6:30
                            // for all other views
                            '': shortTimeformat.replace(/:mm/,'(:mm)')  // 7pm
                        },
                        axisFormat : shortTimeformat.replace(/:mm/,'(:mm)'),
                        weekNumbers: true,
                        daysOfWeek: moment.weekdaysMin(),
                        monthNames: moment.monthsShort(),
                        //monthNames: localeData.months(),
                        monthNamesShort: moment.monthsShort(),
                        dayNames: moment.weekdays(),
                        dayNamesShort: moment.weekdaysShort(),
                        header: {
                            left: 'prev,next today',
                            center: 'title',
                            right: 'month,agendaWeek,agendaDay'
                        },
                        eventAfterRender: function (event, element, view) {
                            if ((view.name !== 'month') && (((event.end-event.start)/60000)<=30)) {
                                //if duration is too small, we see the html code of img
                                var current_title = $(element.find('.fc-event-time')).text();
                                var new_title = current_title.substr(0,current_title.indexOf("<img")>0?current_title.indexOf("<img"):current_title.length);
                                element.find('.fc-event-time').html(new_title);
                            }
                        },
                        eventRender: function (event, element, view) {
                            element.find('.fc-event-title').html(event.title);
                        },
                    }
                    $calendar.fullCalendar(options);


            },
    });



    animation.registry.s_instituut= animation.Class.extend({

            selector: "section.s_instituut",

             ChoiceInstituut :function(){
               var self = this;
               var company=$(this).prop('id');
               $.ajax({
                    url: '/choice/instituut/' + company ,
                    dataType: 'json',
                    success: function(result) {
                      location.reload();
                    },
               });
            },

                start : function() {
                  var o=this;
                  o.$target.find('#L0860_390_097').attr('default',0);
                  o.$target.find('#L0860_390_097').css('background-color','white');
                  o.$target.find('#L0431_896_359').attr('default',0);
                  o.$target.find('#L0431_896_359').css('background-color','white');
                  o.$target.find('#L0420_127_685').attr('default',0);         
                  o.$target.find('#L0420_127_685').css('background-color','white');
                  
                  o.$target.find('#OTHERS').attr('default',0);         
                  o.$target.find('#OTHERS').css('background-color','white');
                  
                  $.ajax({
                       url: '/choice/is_instituut/' + 'L0860_390_097' ,
                       dataType: 'json',
                       success: function(result) {
                          var self = o;
                          if (result.result=="1"){
                             self.$target.find('#L0860_390_097').css('background-color','rgb(212, 230, 242)');
                          }
                          self.$target.find('#L0860_390_097').attr('default',result.result);
                          self.$target.find('#L0860_390_097').on('click', self.ChoiceInstituut);
                          self.$target.find('#L0860_390_097').hover(function() {
                                  $(this).css('cursor','pointer');
                                  $(this).css('background-color','rgb(212, 230, 242)');
                          }, function() {
                                  $(this).css('cursor','auto');
                                  if ($(this).attr('default')=="0"){
                                      $(this).css('background-color','white');
                                  }
                           });
                       },
                  });

                  $.ajax({
                       url: '/choice/is_instituut/' + 'L0431_896_359' ,
                       dataType: 'json',
                       success: function(result) {
                          var self = o;
                          if (result.result=="1"){
                             self.$target.find('#L0431_896_359').css('background-color','rgb(244, 220, 199)');
                          }
                          self.$target.find('#L0431_896_359').attr('default',result.result);
                          self.$target.find('#L0431_896_359').on('click', self.ChoiceInstituut);
                          self.$target.find('#L0431_896_359').hover(function() {
                                  $(this).css('cursor','pointer');
                                  $(this).css('background-color','rgb(244, 220, 199)');
                            }, function() {
                                  $(this).css('cursor','auto');
                                  if ($(this).attr('default')=="0"){
                                      $(this).css('background-color','white');
                                  }
                           });
                       },
                  });


                  $.ajax({
                       url: '/choice/is_instituut/' + 'L0420_127_685' ,
                       dataType: 'json',
                       success: function(result) {
                            var self = o;
                            self.$target.find('#L0420_127_685').attr('default',result.result);
                            if (result.result=="1"){
                               self.$target.find('#L0420_127_685').css('background-color','rgb(212, 236, 203)');
                            }
                            self.$target.find('#L0420_127_685').on('click', self.ChoiceInstituut);
                            self.$target.find('#L0420_127_685').hover(function() {
                                  $(this).css('cursor','pointer');
                                  $(this).css('background-color','rgb(212, 236, 203)');
                            }, function() {
                                  $(this).css('cursor','auto');
                                  if ($(this).attr('default')=="0"){
                                      $(this).css('background-color','white');
                                  }
                           });
                       },
                  });

				  $.ajax({
                       url: '/choice/is_instituut/' + 'OTHERS' ,
                       dataType: 'json',
                       success: function(result) {
                            var self = o;
                            self.$target.find('#OTHERS').attr('default',result.result);
                            if (result.result=="1"){
                               self.$target.find('#OTHERS').css('background-color','#D8BFD8'); /* Turquoise (web colors) */
                            }
                            self.$target.find('#OTHERS').on('click', self.ChoiceInstituut);
                            self.$target.find('#OTHERS').hover(function() {
                                  $(this).css('cursor','pointer');
                                  $(this).css('background-color','#D8BFD8');
                            }, function() {
                                  $(this).css('cursor','auto');
                                  if ($(this).attr('default')=="0"){
                                      $(this).css('background-color','white');
                                  }
                           });
                       },
                  });


                    },


        });
});
