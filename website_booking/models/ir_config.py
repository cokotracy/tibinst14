# -*- coding: utf-8 -*-
# #Copyright (C) Monoyer Fabian (info@olabs.be)                                         #
#                                                                                     #
#Odoo Proprietary License v1.0                                                        #
#                                                                                     #
#This software and associated files (the "Software") may only be used (executed,      #
#modified, executed after modifications) if you have purchased a valid license        #
#from the authors, typically via Odoo Apps, or if you have received a written         #
#agreement from the authors of the Software (see the COPYRIGHT file).                 #
#                                                                                     #
#You may develop Odoo modules that use the Software as a library (typically           #
#by depending on it, importing it and using its resources), but without copying       #
#any source code or material from the Software. You may distribute those              #
#modules under the license of your choice, provided that this license is              #
#compatible with the terms of the Odoo Proprietary License (For example:              #
#LGPL, MIT, or proprietary licenses similar to this one).                             #
#                                                                                     #
#It is forbidden to publish, distribute, sublicense, or sell copies of the Software   #
#or modified copies of the Software.                                                  #
#                                                                                     #
#The above copyright notice and this permission notice must be included in all        #
#copies or substantial portions of the Software.                                      #
#                                                                                     #
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR           #
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,             #
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.                                #
#IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,          #
#DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,     #
#ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER          #
#DEALINGS IN THE SOFTWARE.                                                            #
#######################################################################################

from odoo import api,fields, models


class BookingConfigSettings(models.TransientModel):

    _inherit = 'res.config.settings'


    def _default_booking(self):
        return self.env['booking.config'].search([], limit=1)

    booking=fields.Many2one("booking.config",string="Booking Config",default=_default_booking, required=True)
    booking_name = fields.Char(related='booking.name')
    booking_direction = fields.Char(related='booking.direction')
    booking_format = fields.Selection(related='booking.format',help="Customize the date format.")
    booking_separator = fields.Char(related='booking.separator',help='Customize the separator of range.')
    booking_applyLabel = fields.Char(related='booking.applyLabel',help='String that will be used to the apply button.')
    booking_cancelLabel = fields.Char(related='booking.cancelLabel',help='String that will be used to the cancel button.')
    booking_fromLabel = fields.Char(related='booking.fromLabel',help='String that will be used to the from label.')
    booking_toLabel = fields.Char(related='booking.toLabel',help='String that will be used to the to label.')
    booking_customRangeLabel = fields.Char(related='booking.customRangeLabel',help='String that will be used to the custom button.')
    booking_showWeekNumbers = fields.Boolean(related='booking.showWeekNumbers',help='Show localized week numbers at the start of each week on the calendars.')
    booking_autoUpdateInput = fields.Boolean(related='booking.autoUpdateInput',help="Indicates whether the date range picker should automatically update the value of an element it's attached to at initialization and when the selected dates change.")
    booking_timePicker = fields.Boolean(related='booking.timePicker',help="Allow selection of dates with times, not just dates.")
    booking_tz = fields.Selection(related='booking.tz',required=True,help="Selection of default timezone for your product.")
    booking_defaultTimeFrom = fields.Char(related='booking.defaultTimeFrom',help="Default time for start booking.")
    booking_defaultTimeTo = fields.Char(related='booking.defaultTimeTo',help="Default time for end booking.")
    booking_multiple = fields.Boolean(related='booking.multiple', default=1, help="You can rent the product on a minimum basis. N X days (minimun) which applies from the first day of your reservation.")
    booking_day = fields.Selection([("-1","Free choice"),('0','Monday'),('1','Tuesday'),('2','Wednesday'),('3','Thursday'),('4','Friday'),('5','Saturday'),('6','Sunday')],related='booking.day',help='The first day of your reservation.')
    booking_bsminDay = fields.Integer(related='booking.bsminDay',help='The minimum of day span between the selected start and end dates for high season.')
    booking_avminDay = fields.Integer(related='booking.avminDay',help='The minimum of day span between the selected start and end dates for average season.')
    booking_hsminDay = fields.Integer(related='booking.hsminDay',help='The minimum of day span between the selected start and end dates for low season.')
    booking_minDate = fields.Integer(related='booking.minDate',help='The start of the initially selected date range')
    booking_maxDate = fields.Integer(related='booking.maxDate',help=' The end of the initially selected date range')
    booking_dateRange=fields.One2many(related="booking.dateRange",help="Set predefined date ranges the user can booking or not. Each key is the label for the range, and its value an array with two dates representing the bounds of the range")
    booking_delivery = fields.Boolean(related='booking.delivery',help="Allow the customer to provide a delivery address")
    booking_delay = fields.Integer(related='booking.delay',help='The max of minutes between two draft saleorder for a product book.')
    booking_user_alert=fields.Many2many(related="booking.user_alert",string='Alert if reserved doubly')
