# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.
from odoo import models, fields, api
from datetime import datetime

class SaleReservationWizard(models.TransientModel):

    _name = 'sale.order.reservation.wizard'

    date_start = fields.Date('Start Date', default=datetime.today().date(), required=True)
    date_end = fields.Date('End Date', default=datetime.today().date(), required=True)
    filter_event=fields.Many2one("event.event",string="Event")

    @api.onchange("filter_event")
    def onchange_date(self):
        if self.filter_event:
            self.date_start=self.filter_event.date_begin
            self.date_end=self.filter_event.date_end

    @api.multi
    def open_url(self):
        self.ensure_one()
        #print (self.date_start,self.date_end,self.filter_event.id if self.filter_event else 0)
        return {
                    'type': 'ir.actions.act_url',
                    'url': '/check_page/%s/%s/%s' % (self.date_start,self.date_end,self.filter_event.id if self.filter_event else 0),
                    'target': 'self',
                    'res_id': self.id,
                }



    @api.multi
    def report_checkin_detail(self):
        data = {
            'ids': self.ids,
            'model': "sale.order.reservation.wizard",
            'form': self.read(['date_start', 'date_end'])[0],
        }
        return self.env.ref('website_booking.booking_checkin_details').report_action(self, data=data, config=False)


    @api.multi
    def report_checkout_detail(self):
        data = {
            'ids': self.ids,
            'model': "sale.order.reservation.wizard",
            'form': self.read(['date_start', 'date_end'])[0],
        }
        return self.env.ref('website_booking.booking_checkout_details').report_action(self, data=data, config=False)


    @api.multi
    def report_coocking_detail(self):
        data = {
            'ids': self.ids,
            'model': "sale.order.reservation.wizard",
            'form': self.read(['date_start', 'date_end','filter_event'])[0],
        }
        return self.env.ref('website_booking.booking_cooking_details').report_action(self, data=data, config=False)
