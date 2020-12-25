
# Copyright  2018 Forest and Biomass Romania
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _
from datetime import datetime,timedelta,time


class ReportTestCheckevent(models.AbstractModel):
    _name = "report.booking_report.report_checkevent_qweb"

    def get_check_event(self, event):
        reservation_obj = self.env['sale.order.line']
        event_search = [
                         ('order_id.state','not in',['cancel']),
                         ('event_id',"=",event)
                        ]
        res = reservation_obj.search(event_search).sorted(key=lambda r: r.order_id.partner_id.name)
        result = []
        for r in res:
            if r.order_id not in result:
                result.append(r.order_id)
        return result

    def get_amount(self,order):
        paid=order.amount_total
        if order.invoice_count>0:
            invoices=self.env["account.invoice"].search([('state',"not in",['draft','cancel']),('origin','=',order.name)])
            for invoice in invoices:
                paid-=invoice.amount_total
        if paid <0:
            paid = 0
        return paid

    def get_lang(self, lang):
        if lang=="en_US":
            return "EN"

        if lang=="fr_BE":
            return "FR"

        if lang=="nl_BE":
            return "NL"
        return lang

    def get_date_start(self, order):
        date = ""
        for record in order:
            for line in record.order_line:
                if line.x_start:
                    date = line.x_start
        return date[0:10]

    def get_date_stop(self, order):
        date = ""
        for record in order:
            for line in record.order_line:
                if line.x_end:
                    date = line.x_end
        return date[0:10]


    def get_list_participant(self, event, order_id):
        participant=[]
        registrations = self.env["event.registration"].search([("event_id", "=", event.id),('sale_order_id', '=', order_id.id)])
        for record in registrations:
            participant.append(record.name)
        if not participant:
            participant.append(order_id.partner_id.name)
        return (', ').join(participant)

    def get_room(self,order):
        room=[]
        for record in order:
            for line in record.order_line:
                if line.x_rental :
                    room.append(line.product_id.default_code)
        return (', ').join(room)

    def get_event(self,order):
        event=[]
        for record in order:
            for line in record.order_line:
                if line.event_id.id :
                    event.append(line.event_id.name)
        return (', ').join(event)

    def get_fittedsheet(self,order):
        accessory=[]
        for record in order:
            for line in record.order_line:
                if line.x_rental:
                    room = line.product_id
                    for line2 in record.order_line:
                        if line2.product_id.id in room.accessory_product_ids.mapped("id"):
                            accessory.append(" %s -> %s" % (line.product_id.default_code, line2.product_id.name))
        return (', ').join(accessory)

    @api.multi
    def get_report_values(self, docids, data=None):

        date_start = datetime.strftime(datetime.strptime(data['form'].get('date_start'), '%Y-%m-%d') - timedelta(days=1), '%Y-%m-%d')
        date_end = datetime.strftime(datetime.strptime(data['form'].get('date_end'), '%Y-%m-%d') + timedelta(days=1), '%Y-%m-%d')
        event = data['form'].get('filter_event')[0]

        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id'))

        get_order= self.get_check_event(event)

        docargs = {
                'doc_ids': docids,
                'doc_model': model,
                'data': data,
                'docs': docs,
                'get_list_participant':self.get_list_participant,
                'get_order': get_order,
                'get_room': self.get_room,
                'get_amount': self.get_amount,
                'get_fittedsheet':self.get_fittedsheet,
                'get_lang':self.get_lang,
                'get_date_start':self.get_date_start,
                'get_date_stop':self.get_date_stop,
                'time': time,
        }
        return docargs


