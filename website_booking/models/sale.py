# -*- coding: utf-8 -*-
#######################################################################################
#                                                                                     #
#Copyright (C) Monoyer Fabian (info@olabs.be)                                         #
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
from odoo import models,fields,api,_
from odoo.http import request
from datetime import datetime,date,timedelta
from odoo.exceptions import ValidationError

import logging

_logger = logging.getLogger(__name__)

class SaleLine(models.Model):
    _inherit = "sale.order.line"

    x_rental = fields.Boolean(string="Booking")
    x_is_room_meal = fields.Boolean("Is room/meal", compute="_compute_is_room_meal")
    x_start = fields.Date(string="Check In")
    x_end = fields.Date(string="Check Out")
    x_planning_id = fields.Many2one("planning.slot", string="PLanning Slot", copy=False)

    @api.depends("product_id")
    def _compute_is_room_meal(self):
        for record in self:
            record.x_is_room_meal = False
            if record.product_id and record.product_id.x_is_room or record.product_id.x_is_meal:
                record.x_is_room_meal = True

    @api.onchange("x_start","x_end")
    def onchange_qty(self):
        for record in self:
            if record.x_start and record.x_end:
                record.product_uom_qty = (record.x_end - record.x_start).days
                if record.product_id.x_is_meal:
                    record.product_uom_qty += 1

class Sale(models.Model):
    _inherit = "sale.order"

    def action_confirm(self):
        res = super(Sale,self).action_confirm()
        for record in self:
            for line in record.order_line:
                if line.product_id.x_is_room:
                   #create planning slot
                   my_time = datetime.min.time()
                   start = datetime.combine(line.x_start, my_time).replace(hour=14, minute=0, second=0)
                   end = datetime.combine(line.x_end, my_time).replace(hour=11, minute=0, second=0)
                   #search room dispo
                   room_choice = False
                   for room in line.product_id.x_planning_role_ids:
                       reservation = self.env["planning.slot"].search([('role_id', '=', room.id),('end_datetime','>=',start),('start_datetime','<=',end)])
                       if not reservation:
                          room_choice = room
                   if room_choice:
                       planning = self.env['planning.slot'].create({
                            'employee_id': line.order_id.partner_id.x_employee_id.id,
                            'start_datetime': start,
                            'end_datetime': end,
                            'role_id': room_choice.id,
                            'x_order_id': record.id,
                       })
                       line.x_planning_id = planning.id
                   else:
                       raise ValidationError(_("Sorry, there are no more rooms available for this type of product."))

        return res

    def action_cancel(self):
        res=super(Sale,self).action_cancel()
        for record in self:
            for line in record.order_line:
                if line.x_planning_id:
                   line.x_planning_id.unlink()
        return res

    def _get_line_description(self, order_id, product_id, attributes=None):
        if not attributes:
            attributes = {}

        order = self.sudo().browse(order_id)
        product_context = dict(self.env.context)
        product_context.setdefault('lang', order.partner_id.lang)
        product = self.env['product.product'].with_context(product_context).browse(product_id)

        name = product.display_name

        if product.x_rental:
            name += '\n(%s - %s)' %(request.session.get("booking_start",request.session.get("booking_mindate",False)),request.session.get("booking_end",request.session.get("booking_maxdate",False)))

        # add untracked attributes in the name
        untracked_attributes = []
        for k, v in attributes.items():
            # attribute should be like 'attribute-48-1' where 48 is the product_id, 1 is the attribute_id and v is the attribute value
            attribute_value = self.env['product.attribute.value'].sudo().browse(int(v))
            if attribute_value and not attribute_value.attribute_id.create_variant:
                untracked_attributes.append(attribute_value.name)
        if untracked_attributes:
            name += '\n%s' % (', '.join(untracked_attributes))

        if product.description_sale:
            name += '\n%s' % (product.description_sale)

        return name




    def _cron_cancel_sale_order(self,day=2):
        DATETIME_FORMAT = "%Y-%m-%d"
        date_search=(date.today()-timedelta(days=day)).strftime(DATETIME_FORMAT)
        recordall=self.env["sale.order"].search([('state','in',["draft"]),('write_date','<','%s 00:00:00' % date_search)])
        _logger.info("Search sale order for cancel")
        for record in recordall:
                _logger.info("cancel Sale Order for %s" % record.name)
                record.write({'state': 'cancel'})

    """
                #Si y a une chambre
            #filtrer les chambres libres
            room_choice = []
            for room in rooms:
                # la chambre n'est plus disponible après une certaine date.
                # print (product.x_available_until)
                ok=True
                #if room.x_available_until and event.date_end and event.date_end[0:10] > room.x_available_until:
                #     ok=False
                if ok and event.date_begin and event.date_end:
                     booking = False #request.env['booking.config'].sudo().search([], limit=1)

                     date_begin = "%s %s" % (event.date_begin[0:10], booking.defaultTimeFrom)
                     date_end = "%s %s" % (event.date_end[0:10], booking.defaultTimeTo)
                     from_dt = datetime.strptime(date_begin, DATETIME_FORMAT)+timedelta(days=nbr_days_extra_neg)
                     to_dt = datetime.strptime(date_end, DATETIME_FORMAT)+timedelta(days=nbr_days_extra_pos)
                     tzuser = request.env.user.partner_id.tz or booking.tz
                     start = from_dt.replace(tzinfo=tz.gettz(tzuser))
                     end = to_dt.replace(tzinfo=tz.gettz(tzuser))
                     start = start.astimezone(tz.gettz("UTC")).strftime(DATETIME_FORMAT)
                     end = end.astimezone(tz.gettz("UTC")).strftime(DATETIME_FORMAT)

                     now = datetime.now()
                     now_minus_delay = str(now + timedelta(minutes=-booking.delay))

                     query = [("product_id.id", "=", room.id),
                              ("product_id.x_rental", "=", True),
                              ("x_start", "<=", str(end)), ("x_end", ">=", str(start)),
                               '|',
                               '&', ('order_id.write_date', '>', now_minus_delay), ('order_id.state', '=', "draft"),
                              ('order_id.state', 'not in', ["cancel", "draft"])]

                     orderline = request.env["sale.order.line"].sudo().search_count(query)
                     if orderline == 0:
                        room_choice.append(room)

    """