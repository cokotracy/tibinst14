
odoo.define('website_booking.frontend', function (require) {
'use strict';

var ajax = require('web.ajax');
var core = require('web.core');
var base = require('web_editor.base');
var animation = require('website.content.snippets.animation');
var qweb = core.qweb;
var _t = core._t;

animation.registry.ProductrentalDate = animation.Class.extend({

        selector: "input[class='datepicker form-control']",
          start : function() {
            var self = this;
            ajax.jsonRpc('/shop/booking/config','call', {}).then(function(data) {
                            data=$.parseJSON(data);
                            $('#daterange').daterangepicker(data, function(start, end, label) {
                                if (!data.timePicker){
                                   //Verify if range is date special
                                   //convert data for python

                                   if (start._i instanceof Array) {
                                          var nStart=start.format('YYYY-MM-DD HH:mm:ss');
                                          var nEnd=end.format('YYYY-MM-DD HH:mm:ss');
                                   }
                                    else {
                                          var nStart=start.format('YYYY-MM-DD')+" "+start._i.substring(11,19);
                                          var nEnd=end.format('YYYY-MM-DD')+" "+end._i.substring(11,19);
                                    }

                                   ajax.jsonRpc('/shop/booking/verify','call', {'start':nStart,'end':nEnd}).then(function(result) {
                                         var verify=$.parseJSON(result);
                                         if (verify.result) { //no forcing time
                                            $("#daterange").val('Du '+nStart+" au  "+nEnd);
                                            $("#reserver").attr('href', '/shop/booking?start='+nStart+'&end='+nEnd+'&redirection=/shop/category/accomodation-144');
                                            $("#checkout").attr('href', '/shop/booking?start='+nStart+'&end='+nEnd+'&redirection=/shop/cart');
                                        }
                                        else { //forcing time default
                                             $("#daterange").val('Du '+start.format('YYYY-MM-DD '+data.defaultTimeFrom)+" au  "+end.format('YYYY-MM-DD '+data.defaultTimeTo));
                                             $("#reserver").attr('href', '/shop/booking?start='+start.format('YYYY-MM-DD '+data.defaultTimeFrom)+'&end='+end.format('YYYY-MM-DD '+data.defaultTimeTo)+'&redirection=/shop/category/accomodation-144');
                                             $("#checkout").attr('href', '/shop/booking?start='+start.format('YYYY-MM-DD '+data.defaultTimeFrom)+'&end='+end.format('YYYY-MM-DD '+data.defaultTimeTo)+'&redirection=/shop/cart');

                                        }
                                        });
                                }
                                else{ //datetime picker, user choice time
                                    $("#daterange").val('Du '+start.format('YYYY-MM-DD')+" au  "+end.format('YYYY-MM-DD'));
                                    $("#reserver").attr('href', '/shop/booking?start='+start.format('YYYY-MM-DD HH:mm:ss')+'&end='+end.format('YYYY-MM-DD HH:mm:ss')+'&redirection=/shop/category/accomodation-144');
                                    $("#checkout").attr('href', '/shop/booking?start='+start.format('YYYY-MM-DD HH:mm:ss')+'&end='+end.format('YYYY-MM-DD HH:mm:ss')+'&redirection=/shop/cart');
                                }
                            });
            });


        if ($("body").hasClass("editor_enable")==false){
              Array.prototype.contains = function(obj) {
                var i = this.length;
                while (i--) {
                    if (this[i] == obj) {
                    return true;
                    }
                }
                return false;
            };
        }
        else {
        Array.prototype.contains=""
        }

	      },


    });



});


odoo.define('website_booking.reservation_alert', function (require) {
"use strict";

$(document).ready(function () {
    // If option is enable
    if ($("#alert_reservation").length) {
        $("button#o_payment_form_pay").addClass("hidden");
    }
});

});
