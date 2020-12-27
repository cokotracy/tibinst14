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
import datetime
import pytz
from dateutil import tz
import logging
from datetime import date,timedelta

_logger = logging.getLogger(__name__)

class SaleLine(models.Model):
    _inherit="sale.order.line"

    x_rental = fields.Boolean(string="Booking")
    x_start = fields.Datetime(string="Check In")
    x_end = fields.Datetime(string="Check Out")
    x_calendar_id=fields.Many2one('calendar.event',string="Event calendar") #compute="onchange_date")
    x_pricelist_id=fields.Many2one('product.pricelist',string="Pricelist")

    @api.model
    def _cron_get_doubly_sale(self):
        result = {}
        rcontext = {}
        rooms=self.env["product.product"].search([('x_is_room','=',True)])
        current_date = datetime.datetime.now().date()
        new_date = current_date + datetime.timedelta(days=+365)
        listdate=[]
        sale_summary={}
        for i in range(0,365):
            listdate.append(current_date + datetime.timedelta(days=i))
        for room in rooms:
                values=[]
                for date in listdate:
                         AM = datetime.datetime.strptime(str(date)+" 00:00:01","%Y-%m-%d %H:%M:%S")

                         queryAM=[("product_id.id","=",room.id),
                         ("product_id.x_rental", "=", True),
                         ("x_end", ">",str(AM)),("x_start", "<", str(AM)),
                         ('order_id.state', 'not in', ["cancel","sent","draft"])]

                         salelines=self.env["sale.order.line"].search(queryAM)
                         if len(salelines)>1:
                             for saleline in salelines:
                                 orderlist=sale_summary.get(room,[])
                                 if saleline.order_id not in orderlist:
                                      orderlist.append(saleline.order_id)
                                      sale_summary.update({room:orderlist})

        for  room, orders in sale_summary.items():
            for order in orders:
                if order.partner_id not in room.x_partner_ids :
                    for user in self.env['booking.config'].sudo().search([],limit=1).user_alert:
                        activity = self.env['mail.activity'].sudo().create({
                                'activity_type_id': self.env.ref('website_booking.mail_activity_urgent').id,
                                'note': _('The room is seems to be overcrowded.The order should be adjusted with a room still available.'),
                                'res_id':  order.id,
                                'user_id': user.id,
                                'res_model_id': self.env.ref('sale.model_sale_order').id,
                                })
                        activity._onchange_activity_type_id()

    @api.onchange("x_start","x_end")
    def onchange_qty(self):
        for record in self:
            if record.x_start and record.x_end:
                from_dt = datetime.datetime.strptime(record.x_start[0:10], "%Y-%m-%d")
                to_dt = datetime.datetime.strptime(record.x_end[0:10], "%Y-%m-%d")
                timedelta = to_dt - from_dt
                seconds = float(timedelta.days * (24 * 60 * 60))
                if record.product_id.uom_id.factor_inv > 0:
                    qty = ((seconds + timedelta.seconds) / record.product_id.uom_id.factor_inv)
                else:
                    qty = (seconds + timedelta.seconds)
                record.product_uom_qty=qty


class Sale(models.Model):
    _inherit="sale.order"
    
    
    #vérifie si le panier contient une chambre sans event. => refuser

    def room_without_event(self):
        self.ensure_one()
        chambre=False
        event=False
        for line in self.order_line:
            if line.product_id.x_is_room:
                chambre=True
            if line.product_id.event_ok:
               event=True
        if chambre==True and event==False:
           return True     
        return False
        
    
    #vérifie si le panier contient que des produits de la même société
    def _verify_company(self):
        self.ensure_one()
        ok=True
        company_id=request.env.user.company_id.id
        if company_id!=self.company_id.id:
            ok=False
        for line in self.order_line:
            if line.product_id.company_id and line.product_id.company_id.id!=company_id:
                ok=False
        return ok       
                
    def _reservation(self):
        self.ensure_one()
        DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
        booking = request.env['booking.config'].sudo().search([],limit=1)
        for line in self.order_line:
            if line.product_id.x_rental:
                if line.x_start and line.x_end:

                    from_dt = datetime.datetime.strptime(line.x_start, DATETIME_FORMAT)
                    to_dt = datetime.datetime.strptime(line.x_end, DATETIME_FORMAT)
                    tzuser = request.env.user.partner_id.tz or booking.tz
                    start = from_dt.replace(tzinfo=tz.gettz(tzuser))
                    end = to_dt.replace(tzinfo=tz.gettz(tzuser))
                    start = start.astimezone(tz.gettz("UTC")).strftime(DATETIME_FORMAT)
                    end = end.astimezone(tz.gettz("UTC")).strftime(DATETIME_FORMAT)
                    now = datetime.datetime.now()
                    now_minus_delay = str(now + datetime.timedelta(minutes = -booking.delay))
                    follow=True
                    if line.product_id and line.product_id.x_is_room:

                        #La chambre est toujours libre pour les partenaires qui sont liés au produit.
                        if self.env.user.partner_id in line.product_id.x_partner_ids:
                            follow=False
                        #la chambre n'est plus disponible après une certaine date.
                        if line.product_id.x_available_until and end[0:10]>line.product_id.x_available_until:
                            follow=True

                    query=[("product_id.product_tmpl_id.id","=",line.product_id.id),
                    ("product_id.x_rental", "=", True),
                    ("x_start", "<=", str(end)), ("x_end", ">=",str(start)),
                    '|',
                    '&','&',('order_id.write_date', '>', now_minus_delay),('order_id.id', '!=',self.id), ('order_id.state', '=', "draft"),
                    ('order_id.state', 'not in', ["cancel", "draft"])]

                    orderline=self.env["sale.order.line"].sudo().search(query)
                    #si la chambre doit vérifiée!
                    if follow and len(orderline)>0:
                        return [True,', '.join(orderline.mapped("product_id.name"))]
                    
        return [False,""]

    def _cart_find_product_line(self, product_id=None, line_id=None, **kwargs):
        self.ensure_one()
        lines = super(Sale, self)._cart_find_product_line(product_id, line_id)
        if line_id:
            return lines

        linked_line_id = kwargs.get('linked_line_id', False)
        optional_product_ids = set(kwargs.get('optional_product_ids', []))

        lines = lines.filtered(lambda line: line.linked_line_id.id == linked_line_id)

        if optional_product_ids:
            # only match the lines with the same chosen optional products on the existing lines
            lines = lines.filtered(lambda line: optional_product_ids == set(line.mapped('option_line_ids.product_id.id')))
        else:
            lines = lines.filtered(lambda line: not line.option_line_ids)

        product=self.env['product.product'].browse(product_id)
        if product.x_is_room:
            lines=self.env["sale.order.line"]
        return lines

    def action_confirm(self):
        res=super(Sale,self).action_confirm()
        for record in self:
            for line in record.order_line:
                if line.x_rental :
                          event = self.env['calendar.event'].search([('x_order_line_id', '=', record.id)])
                          data = {
                                'name': "%s - %s" % (record.partner_id.name, line.product_id.name),
                                'start_datetime': line.x_start,
                                'start': line.x_start,
                                'stop': line.x_end,
                                'partner_ids': [(6, 0, [record.partner_id.id])],
                                'x_order_line_id': line.id,
                                }
                          if event:
                              event.with_context(no_mail_to_attendees=True).write(data)
                          else:
                              event=event.with_context(no_mail_to_attendees=True).create(data)
                          line.x_calendar_id=event.id
        return res

    def action_cancel(self):
        res=super(Sale,self).action_cancel()
        for record in self:
            for line in record.order_line:
                if line.x_rental :
                   event = self.env['calendar.event'].search([('x_order_line_id', '=', line.id)])
                   data = {
                      'active':False,
                   }
                   event.with_context(no_mail_to_attendees=True).write(data)
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


    def _booking_delivery(self):
        booking = self.env['booking.config'].sudo().search([], limit=1)
        for order in self:
            for line in order.order_line:
                if line.product_id.x_rental:
                    return booking.delivery
        return True


    def _cron_cancel_sale_order(self,day=2):
        DATETIME_FORMAT = "%Y-%m-%d"
        date_search=(date.today()-timedelta(days=day)).strftime(DATETIME_FORMAT)
        recordall=self.env["sale.order"].search([('state','in',["draft"]),('write_date','<','%s 00:00:00' % date_search)])
        _logger.info("Search sale order for cancel")
        for record in recordall:
                _logger.info("cancel Sale Order for %s" % record.name)
                record.write({'state': 'cancel'})

