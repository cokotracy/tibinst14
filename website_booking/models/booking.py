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
from odoo.addons.base.res.res_partner import _tz_get
from odoo import api, fields, models

class BookingDate(models.Model):
    _name="booking.date"

    name=fields.Char("Name", translate=True)
    dateStart=fields.Datetime(string="Date Start")
    dateStop=fields.Datetime(string='Date End')
    type=fields.Selection([('range','Range'),('deactivate','Deactivate')],string="Type")
    config_id=fields.Many2one("booking.config","dateRange")

class BookingConfig(models.Model):
    _name="booking.config"

    name=fields.Char(string="Name",required=True)
    direction = fields.Char(string="Direction", default="ltr")
    format = fields.Selection([('DD/MM/YYYY HH:mm:ss','DD/MM/YYYY'),('DD-MM-YYYY HH:mm:ss','DD-MM-YYYY'),('MM-DD-YYYY HH:mm:ss','MM-DD-YYYY'),('YYYY-MM-DD HH:mm:ss','YYYY-MM-DD')],string='Date format', default="YYYY-MM-DD HH:mm:ss")
    separator = fields.Char(string='Separator', default="-")
    applyLabel = fields.Char(string='Apply label', default="Apply",translate=True)
    cancelLabel = fields.Char(string='cancel Label', default="Cancel",translate=True)
    fromLabel = fields.Char(string='From Label', default="From",translate=True)
    toLabel = fields.Char(string='To Label', default="To",translate=True)
    customRangeLabel = fields.Char(string='custom Range Label', default="")
    showWeekNumbers = fields.Boolean(string='show Week Numbers', default=True)
    autoUpdateInput = fields.Boolean(string='auto Update Input', default=False)
    timePicker = fields.Boolean(string='time Picker', default=False)
    defaultTimeFrom=fields.Char(string='default Time From', default="22:00:00")
    defaultTimeTo=fields.Char(string='default Time To', default="22:00:00")
    tz = fields.Selection(_tz_get, 'Timezone', size=64, required=True,help="The product's timezone, used to output proper date and time values inside printed reports. ""It is important to set a value for this field. ")
    multiple = fields.Boolean(string='multiple', default=False)
    day = fields.Selection([("-1","Free choice"),('0','Monday'),('1','Tuesday'),('2','Wednesday'),('3','Thursday'),('4','Friday'),('5','Saturday'),('6','Sunday')],string='Day', default="-1")
    bsminDay = fields.Integer(string='Low Season minimum Day', default=1)
    avminDay = fields.Integer(string='Average Season minimum Day', default=1)
    hsminDay = fields.Integer(string='High Season minimum Day', default=1)
    minDate = fields.Integer(string='minimun Date', default=1)
    maxDate = fields.Integer(string='maximun Date', default=365)
    dateRange=fields.One2many("booking.date","config_id",string='date Range')
    delivery = fields.Boolean(string='Delivery', default=False)
    delay = fields.Integer(string='Delay', default=10)
    user_alert=fields.Many2many("res.users","config_id",string='Alert if reserved doubly')

    def date(self, time=True):
        newFormat = self.format
        newFormat = newFormat.replace("YYYY", "%Y")
        newFormat = newFormat.replace("MM", "%m")
        newFormat = newFormat.replace("DD", "%d")
        newFormat = newFormat.replace("HH", "%H")
        newFormat = newFormat.replace("mm", "%M")
        newFormat = newFormat.replace("ss", "%S")
        if not time:
            return newFormat[0:8]
        return newFormat
