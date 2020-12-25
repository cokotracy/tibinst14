#coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) Monoyer Fabian (info@olabs.be)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from datetime import datetime,timedelta,date
from odoo import fields, http, tools, _
from odoo.http import request

class Website_Check(http.Controller):


    def get_checkin(self, date_start, date_end,event_id):
        reservation_obj = request.env['sale.order.line']
        sale_obj = request.env['sale.order']
        if event_id>0:
            event_search = [
                        ('event_ok',"=",True),
                        ('event_id.id', '=', event_id),
                      ]
        else :
            event_search = [
                        ('event_ok',"=",True),
                        ('event_id.date_begin', '>=', '%s 00:00:01' %(date_start)),
                        ('event_id.date_end', '<=', '%s 23:59:59' %(date_end)),
                      ]
        res = reservation_obj.search(event_search).mapped("order_id.id")
        res = sale_obj.browse(res).sorted(key=lambda r: r.partner_id.name)
        return res

    def get_state(self,order):
        paid=_("No Paid")
        by=""
        if order.payment_transaction_count>0:
            payment=request.env["payment.transaction"].search([('reference','=',order.name)])
            by=payment.acquirer_id.name
            paid=payment.state

        elif order.invoice_count>0:
            invoice=request.env["account.invoice"].search([('origin','=',order.name)])
            by=_("invoice")
            paid=invoice[0].state

        return [order.state,by, paid]

    def get_name(self, reg):
        partner=request.env["res.partner"].sudo().search([('barcode','=',reg.barcode)]) or request.env["res.partner"].sudo().search([('email','=',reg.email)])
        if partner:
            return "%s (%s -  %s)" % (reg.name,partner[0].email,partner[0].name)
        else:
            return "%s (%s -  %s)" % ("Inconnu",reg.name,reg.email)
            
    def get_lang(self, lang):
        if lang=="en_US":
            return "EN"

        if lang=="fr_BE":
            return "FR"

        if lang=="nl_BE":
            return "NL"
        return lang

    def get_event(self,order):
        event=[]
        for record in order:
            for line in record.order_line:
                if line.event_id and line.event_id.name not in event:
                    event.append(line.event_id.name)
        #print(event)
        if event:
            return (', ').join(event)
        else :
            return ''

    def get_fittedsheet(self,order):
        accessory=[]
        for record in order:
            for line in record.order_line:
                if line.product_id.id in request.env["product.product"].search([('id','in',order.order_line.mapped('product_id.id'))]).mapped("accessory_product_ids.id"):
                    accessory.append('%s (%s)'% (line.product_id.name,int(line.product_uom_qty)))
        return (', ').join(accessory)

    def get_room(self,order):
        room=[]
        for record in order:
            for line in record.order_line:
                if line.product_id.x_is_room:
                    if line.product_id.default_code:
                        room.append(line.product_id.default_code)
        return (', ').join(room)

    def get_registration(self,sale):
        registration=request.env["event.registration"].search([('sale_order_id','=',sale)])
        return registration

    def get_date(self, order,typ):
        for record in order:
            for line in record.order_line:
                if line.product_id.x_rental:
                    if typ=="in":
                     if line.x_start:
                         return line.x_start[0:10]
                    else :
                     if line.x_end:
                         return line.x_end[0:10]
            #si pas de date cherche les date de l'event
            for line in record.order_line:
                if line.event_id:
                    if typ=="in":
                     if line.event_id.date_begin:
                         return line.event_id.date_begin[0:10]
                    else :
                     if line.event_id.date_end:
                         return line.event_id.date_end[0:10]

        return ""


    def get_night(self, order):
        for record in order:
            for line in record.order_line:
                if line.product_id.x_is_room:
                    return int(line.product_uom_qty)


    @http.route(['/check_page/<string:begin>/<string:end>/<int:event_id>'], type='http', auth="user", website=True)
    def page(self,begin,end,event_id):
            date=datetime.now()
            if not begin:
                begin=(date+timedelta(days=-20)).strftime("%Y-%m-%d")
            if not end:
                end=(date+timedelta(days=+20)).strftime("%Y-%m-%d")
            get_checkin = self.get_checkin(begin,end,event_id)
            values = {
                    'begin':begin,
                    'end':end,
                    'event_id':event_id,
                    'get_checkin': get_checkin,
                    'get_fittedsheet':self.get_fittedsheet,
                    'get_lang':self.get_lang,
                    'get_event':self.get_event,
                    'get_night':self.get_night,
                    'get_state':self.get_state,
                    'get_date':self.get_date,
                    'get_room':self.get_room,
                    'get_name':self.get_name,
                    'get_registration':self.get_registration,
            }
            return request.render('website_booking.check_page', values)



