
# Copyright  2018 Forest and Biomass Romania
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _
from datetime import datetime,timedelta,time

class ReportTestCheckin(models.AbstractModel):
    _name = "report.website_booking.report_checkin_qweb"



    def get_checkin(self, date_start, date_end):
        reservation_obj = self.env['sale.order.line']
        room_search = [
                        ('order_id.state','not in',['draft']),
                        ('x_rental',"=",True),
                        ('x_start', '>=', '%s 00:00:01' %(date_start)),
                        ('x_start', '<=', '%s 23:59:59' %(date_end)),
                      ]
        res = reservation_obj.search(room_search).sorted(key=lambda r: r.order_id.partner_id.name)
        return res

    def get_state(self,order):
        paid=_("No Paid")
        by=""
        if order.payment_transaction_count>0:
            payment=self.env["payment.transaction"].search([('reference','=',order.name)])
            by=payment.acquirer_id.name
            paid=payment.state

        elif order.invoice_count>0:
            invoice=self.env["account.invoice"].search([('origin','=',order.name)])
            by=_("invoice")
            paid=invoice.state

        return [order.state,by, paid]

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
                if line.event_id.id :
                    event.append(line.event_id.name)
        return (',').join(event)

    def get_date(self, date):
        return date[0:10]

    def get_fittedsheet(self,order,room):
        accessory=[]
        for record in order:
            for line in record.order_line:
                if line.product_id.id in room.accessory_product_ids.mapped("id"):
                    accessory.append(line.product_id.name)
        return (',').join(accessory)

    def get_report_values(self, docids, data=None):

        date_start = data['form'].get('date_start')
        date_end = data['form'].get('date_end')
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id'))

        get_checkin = self.get_checkin(date_start,date_end)

        docargs = {
                'doc_ids': docids,
                'doc_model': model,
                'data': data,
                'docs': docs,
                'get_checkin': get_checkin,
                'get_fittedsheet':self.get_fittedsheet,
                'get_lang':self.get_lang,
                'get_date':self.get_date,
                'get_event':self.get_event,
                'get_state':self.get_state,
                'time': time,
        }
        return docargs


class ReportTestCheckout(models.AbstractModel):
    _name = "report.website_booking.report_checkout_qweb"



    def get_checkout(self, date_start, date_end):
        reservation_obj = self.env['sale.order.line']
        room_search = [
                        ('order_id.state','not in',['cancel']),
                        ('x_rental',"=",True),
                        ('x_end', '>=', '%s 00:00:01' %(date_start)),
                        ('x_end', '<=', '%s 23:59:59' %(date_end)),
                      ]
        res = reservation_obj.search(room_search).sorted(key=lambda r: r.order_id.partner_id.name)
        return res

    def get_state(self,order):
        paid=_("No Paid")
        by=""
        if order.payment_transaction_count>0:
            payment=self.env["payment.transaction"].search([('reference','=',order.name)])
            by=payment.acquirer_id.name
            paid=payment.state

        elif order.invoice_count>0:
            invoice=self.env["account.invoice"].search([('origin','=',order.name)])
            by=_("invoice")
            paid=invoice.state

        return [order.state,by, paid]

    def get_lang(self, lang):
        if lang=="en_US":
            return "EN"

        if lang=="fr_BE":
            return "FR"

        if lang=="nl_BE":
            return "NL"
        return lang

    def get_date(self, date):
        return date[0:10]

    def get_event(self,order):
        event=[]
        for record in order:
            for line in record.order_line:
                if line.event_id.id :
                    event.append(line.event_id.name)
        return (',').join(event)

    def get_fittedsheet(self,order,room):
        accessory=[]
        for record in order:
            for line in record.order_line:
                if line.product_id.id in room.accessory_product_ids.mapped("id"):
                    accessory.append(line.product_id.name)
        return (',').join(accessory)

    def get_report_values(self, docids, data=None):

        date_start = data['form'].get('date_start')
        date_end = data['form'].get('date_end')
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id'))

        get_checkout = self.get_checkout(date_start,date_end)

        docargs = {
                'doc_ids': docids,
                'doc_model': model,
                'data': data,
                'docs': docs,
                'get_checkout': get_checkout,
                'get_fittedsheet':self.get_fittedsheet,
                'get_event':self.get_event,
                'get_lang':self.get_lang,
                'get_date':self.get_date,
                'get_state':self.get_state,
                'time': time,
        }
        return docargs

class ReportTestCoocking(models.AbstractModel):
    _name = "report.website_booking.report_cooking_qweb"

    def get_cooking(self, date_start, date_end,event_id):
        #search meal
        sale_obj = self.env['sale.order']
        room_search = [ ('state','not in',['draft','cancel']),
                        ('create_date','<=',date_end),
                        ]
        res = sale_obj.search(room_search)
        DATETIME_FORMAT = "%Y-%m-%d"

        table=[]
        cooking={}
        eventlist=[]
        for sale in res:
            for line in sale.order_line:
                iflunch=False
                x_capacity=0
                if line.event_id :
                     count=1
                     if event_id and line.event_id!=event_id:
                        count=0
                     #si un event, regarder si des repas sont linké à l'event dans la sale order
                     if count:
                         for line2 in sale.order_line:
                          if line2.product_id.x_is_meal:
                             if line2.linked_line_id.event_id:
                                iflunch=True
                         start=line.event_id.date_begin
                         end=line.event_id.date_end
                         x_capacity=int(line.product_uom_qty)
                         if start and end:
                            start_dt = datetime.strptime(start[0:10], DATETIME_FORMAT)
                            end_dt = datetime.strptime(end[0:10], DATETIME_FORMAT)
                            delta = end_dt - start_dt # timedelta
                            for i in range(delta.days + 1):
                                days=(start_dt + timedelta(days=i)).strftime(DATETIME_FORMAT)
                                if days>=date_start and end[0:10]<=date_end :
                                    if days not in table:
                                        cooking.update({days:{
                                        'Breakfast':0,
                                        'Lunch':0,
                                        'Supper':0,
                                        #'Vegetarian':0
                                        }})
                                        table.append(days)
                                    if iflunch:
                                        val=(cooking[days]).get("Lunch",0)+x_capacity
                                        (cooking[days]).update({"Lunch":val})
                                    #if vegetarian>0:
                                    #   val=(cooking[days]).get("Vegetarian",0)+(vegetarian)
                                    #  (cooking[days]).update({"Vegetarian":val})
                iflunch=False
                ifbreakfast=False
                ifsupper=False
                #Regarde si dans la location des repas sont compris
                if line.product_id.x_rental:
                   # si logement les repas sont obligatoires !!!
                   iflunch=True
                   ifbreakfast=True
                   ifsupper=True
                   # le nombre de personne de la chambre va définir le nombre de repas
                   x_capacity=line.product_id.x_capacity
                   # de date à date
                   start=line.x_start
                   end=line.x_end
                   if start and end :
                    start_dt = datetime.strptime(start[0:10], DATETIME_FORMAT)
                    end_dt = datetime.strptime(end[0:10], DATETIME_FORMAT)
                    delta = end_dt - start_dt  # timedelta
                    for i in range(delta.days + 1):
                        days=(start_dt + timedelta(days=i)).strftime(DATETIME_FORMAT)
                        if days>=date_start and end[0:10]<=date_end :
                            if days not in table:
                                cooking.update({days:{
                                'Breakfast':0,
                                'Lunch':0,
                                'Supper':0,
                                #'Vegetarian':0
                                }})
                                table.append(days)
                            #Le premier jours, le souper
                            if i==0:
                                val=(cooking[days]).get("Supper",0)+x_capacity
                                (cooking[days]).update({"Supper":val})
                            #Le dernier jours le déjeuner
                            elif i==(delta.days):
                                val=(cooking[days]).get("Breakfast",0)+x_capacity
                                (cooking[days]).update({"Breakfast":val})
                            # les autres jours, le déjeuner, le lunch, le souper
                            else:
                                val=(cooking[days]).get("Breakfast",0)+x_capacity
                                (cooking[days]).update({"Breakfast":val})
                                val=(cooking[days]).get("Lunch",0)+x_capacity
                                (cooking[days]).update({"Lunch":val})
                                val=(cooking[days]).get("Supper",0)+x_capacity
                                (cooking[days]).update({"Supper":val})



        return sorted(table),cooking

    def get_state(self,order):
        paid=_("No Paid")
        by=""
        if order.payment_transaction_count>0:
            payment=self.env["payment.transaction"].search([('reference','=',order.name)])
            by=payment.acquirer_id.name
            paid=payment.state

        elif order.invoice_count>0:
            invoice=self.env["account.invoice"].search([('origin','=',order.name)])
            by=_("invoice")
            paid=invoice.state

        return [order.state,by, paid]

    def get_fittedsheet(self,order,room):
        accessory=[]
        for record in order:
            for line in record.order_line:
                if line.product_id.id in room.accessory_product_ids.mapped("id"):
                    accessory.append(line.product_id.name)
        return (',').join(accessory)

    def get_report_values(self, docids, data=None):

        date_start = data['form'].get('date_start')
        date_end = data['form'].get('date_end')
        event_id = data['form'].get('filter_event')
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id'))

        get_key,get_cooking = self.get_cooking(date_start,date_end,event_id)
        docargs = {
                'doc_ids': docids,
                'doc_model': model,
                'data': data,
                'docs': docs,
                'get_cooking': get_cooking,
                'get_key': get_key,
                'get_fittedsheet':self.get_fittedsheet,
                'get_state':self.get_state,
                'time': time,
        }
        return docargs
