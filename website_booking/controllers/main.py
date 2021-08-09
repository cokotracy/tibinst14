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
import json
import pytz
import werkzeug
from dateutil import tz
from datetime import datetime,timedelta,date
from odoo import fields, http, tools, _
from odoo.http import request
from odoo.tools import safe_eval
from dateutil.relativedelta import relativedelta
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.addons.website_event.controllers.main import WebsiteEventController
from odoo.addons.portal.controllers.portal import CustomerPortal,get_records_pager
from odoo.addons.sale_subscription.controllers.portal import sale_subscription
from odoo.addons.http_routing.models.ir_http import slug, unslug

import random


class sale_subscription(sale_subscription):

    @http.route()
    def subscription(self, account_id, uuid='', message='', message_class='', **kw):
        account_res = request.env['sale.subscription']
        if uuid:
            account = account_res.sudo().browse(account_id)
            if uuid != account.uuid or account.state == 'cancelled':
                raise NotFound()
            if request.uid == account.partner_id.user_id.id:
                account = account_res.browse(account_id)
        else:
            account = account_res.browse(account_id)

        acquirers = list(request.env['payment.acquirer'].search([
            ('website_published', '=', True),
            ('registration_view_template_id', '!=', False),
            ('token_implemented', '=', True),
            ('company_id', '=', account.company_id.id),
            ]))
        acc_pm = account.payment_token_id
        part_pms = account.partner_id.payment_token_ids
        display_close = account.template_id.sudo().user_closable and account.state != 'close'
        is_follower = request.env.user.partner_id.id in [follower.partner_id.id for follower in account.message_follower_ids]
        active_plan = account.template_id.sudo()
        periods = {'daily': 'days', 'weekly': 'weeks', 'monthly': 'months', 'yearly': 'years'}
        if account.recurring_rule_type != 'weekly':
            rel_period = relativedelta(datetime.today(), datetime.strptime(account.recurring_next_date, '%Y-%m-%d'))
            missing_periods = getattr(rel_period, periods[account.recurring_rule_type]) + 1
        else:
            delta = datetime.today() - datetime.strptime(account.recurring_next_date, '%Y-%m-%d')
            missing_periods = delta.days / 7
        dummy, action = request.env['ir.model.data'].get_object_reference('sale_subscription', 'sale_subscription_action')
        values = {
            'account': account,
            'template': account.template_id.sudo(),
            'display_close': display_close,
            'is_follower': is_follower,
            'close_reasons': request.env['sale.subscription.close.reason'].search([]),
            'missing_periods': missing_periods,
            'payment_mandatory': active_plan.payment_mandatory,
            'user': request.env.user,
            'acquirers': acquirers,
            'acc_pm': acc_pm,
            'part_pms': part_pms,
            'is_salesman': request.env['res.users'].sudo(request.uid).has_group('sales_team.group_sale_salesman'),
            'action': action,
            'message': message,
            'message_class': message_class,
            'change_pm': kw.get('change_pm') != None,
            'pricelist': account.pricelist_id.sudo(),
            'submit_class':'btn btn-primary btn-sm mb8 mt8 pull-right',
            'submit_txt':'Pay Subscription',
            'bootstrap_formatting':True,
            'return_url':'/my/subscription/' + str(account_id) + '/' + str(uuid),
        }
        history = request.session.get('my_subscriptions_history', [])
        values.update(get_records_pager(history, account))
        return request.render("sale_subscription.subscription", values)


class CustomerPortal(CustomerPortal):


    @http.route(['/my/account/company'], type='http', auth='user', website=True)
    def my_company(self,company):
        if int(company) in request.env.user.company_ids.mapped("id"):
                request.env.user.company_id=int(company)
        values = self._prepare_portal_layout_values()
        return request.render("portal.portal_my_home", values)


class WebsiteEventSaleController(WebsiteEventController):

    @http.route(['/event/<model("event.event"):event>/registration/error/<int:error_number>'], type='http', auth="public", website=True)
    def registration_error(self, event,error_number):
        if error_number == 1:
           error=_("Only one registration per person is allowed !")
        if error_number == 2:
            error=_("It seems that there are no more rooms in this category available, please change the room category or call the centre for more details.")
        if error_number == 3:
            error=_("To make a reservation for an event, you must log in to your account and provide login/password.")
        data = {"event": event, "error":error}
        return request.render("website_booking.error", data)

    @http.route(['/event/<model("event.event"):event>/registration/confirm'], type='http', auth="public", methods=['POST'], website=True)
    def registration_confirm(self, event, **post):
        #clean order
        if request.env.user.id in request.env['res.users'].sudo().search([('active','=',False), ('name', 'ilike', 'Public user')]).ids :
            return request.redirect('/event/%s/registration/error/3' % slug(event))

        order = request.website.sale_get_order()
        request.website.sale_reset()
        if order:
            order.sudo().unlink()
        order = request.website.sale_get_order(force_create=1)
        attendee_ids = set()
        registrations = self._process_attendees_form(event, post)
        barcode_list = []

        for registration in registrations:
            if registrations.count(registration) > 1:
                return request.redirect('/event/%s/registration/error/1' % slug(event))

        for registration in registrations:
            #pour chaque enregistrement
            # update ajouter l'adresse email
            # le nom, le phone
            # et sauver le barcode dans un champ pour la liste de prix
            registration["barcode"] = registration["name"]
            partner_price = request.env["res.partner"].sudo().search([('x_barcode', '=', registration['barcode'])])
            registration["name"] = partner_price[0].name
            registration["phone"] = partner_price[0].phone
            registration["email"] = partner_price[0].email
            nbr_days_night = (event.date_end.replace(hour=23, minute=59, second=59, microsecond=0)-event.date_begin.replace(hour=0, minute=0, second=1, microsecond=0)).days
            nbr_days_events = nbr_days_night + 1
            nbr_days_extra = 0
            extra_rooms = False
            extra_meals = []
            nbr_days_extra_neg = 0
            nbr_days_extra_pos = 0
            for key, values in registration.items():
                if key == 'registration_answer_ids':
                    for value in values:
                        answer_id = value[2].get("value_answer_id", False)
                        answer = request.env["event.question.answer"].browse(answer_id)
                        #ajoute les nuits supplémentaires, en cas de logement...
                        nbr_days_extra += abs(answer.x_days)
                        if answer.x_days < 0:
                            nbr_days_extra_neg += answer.x_days
                        else:
                            nbr_days_extra_pos += answer.x_days

                        if answer.x_meal_ids:
                            #ajoute les produits extra
                            extra_meals += answer.x_meal_ids.mapped("id")
                        if answer.x_room_id:
                            extra_rooms = answer.x_room_id

            ticket = request.env['event.event.ticket'].sudo().browse(int(registration['event_ticket_id']))

            if partner_price and registration['barcode'] not in barcode_list:
                barcode_list.append(registration['barcode'])

            #ajouter la reservation de l'event + les repas lunch
            cart_values = order.with_context(event_ticket_id=ticket.id, fixed_price=True)._cart_update(product_id=ticket.product_id.id, add_qty=1, registration_data=[registration])
            for product in ticket.event_id.x_product:
                cart_values2 = order._cart_update(product_id=product.id, linked_line_id=cart_values["line_id"],
                                                  add_qty=nbr_days_events, attributes='',
                                                  optional_product_ids=[ticket.product_id.id])

                SaleOrderLineSudo = request.env['sale.order.line'].sudo().browse([cart_values2['line_id']])
                SaleOrderLineSudo.write({'name': '%s\n' % (SaleOrderLineSudo.product_id.description_sale or SaleOrderLineSudo.product_id.name)})

            capacity = 1

            if extra_rooms:
                my_time = datetime.min.time()
                start = datetime.combine(event.date_begin + timedelta(days=nbr_days_extra_neg), my_time).replace(hour=14, minute=0, second=0)
                end = datetime.combine(event.date_end + timedelta(days=nbr_days_extra_pos), my_time).replace(hour=11, minute=0, second=0)
                # search room dispo
                room_dispo = False
                for room in extra_rooms.x_planning_role_ids:
                    reservation = request.env["planning.slot"].search(
                        [('role_id', '=', room.id), ('end_datetime', '>=', start), ('start_datetime', '<=', end)])
                    if not reservation:
                        room_dispo = True

                if not room_dispo:
                    return request.redirect('/event/%s/registration/error/2' % slug(event))

                capacity = extra_rooms.x_capacity
                #add room
                cart_values2 = order._cart_update(product_id=extra_rooms.id, linked_line_id=cart_values["line_id"],
                                                      add_qty=(nbr_days_night+nbr_days_extra), attributes='',
                                                      optional_product_ids=[ticket.product_id.id])
                SaleOrderLineSudo = request.env['sale.order.line'].sudo().browse([cart_values2['line_id']])
                SaleOrderLineSudo.write({'x_rental': True, 'x_start': event.date_begin + timedelta(days=nbr_days_extra_neg), 'x_end':event.date_end + timedelta(days=nbr_days_extra_pos), 'name': '%s\nEvent: %s day(s)\nExtra: %s day(s)\n' % (SaleOrderLineSudo.product_id.description_sale or SaleOrderLineSudo.product_id.name ,nbr_days_night, nbr_days_extra)})
                #add breakfast
                breakfast = request.env.ref("website_booking.product_breakfast")
                evening = request.env.ref("website_booking.product_evening")
                cart_values2 = order._cart_update(product_id=breakfast.id, linked_line_id=cart_values["line_id"],
                                                      add_qty=capacity*(nbr_days_night+nbr_days_extra), attributes='',
                                                      optional_product_ids=[ticket.product_id.id])
                SaleOrderLineSudo = request.env['sale.order.line'].sudo().browse([cart_values2['line_id']])
                SaleOrderLineSudo.write({'x_rental': True, 'x_start': event.date_begin + timedelta(days=nbr_days_extra_neg), 'x_end':event.date_end + timedelta(days=nbr_days_extra_pos), 'name': '%s\nEvent: %s day(s)\nExtra: %s day(s)\n' % (SaleOrderLineSudo.product_id.description_sale or SaleOrderLineSudo.product_id.name ,nbr_days_night, nbr_days_extra)})
                #add evening
                cart_values2 = order._cart_update(product_id=evening.id, linked_line_id=cart_values["line_id"],
                                                      add_qty=capacity*(nbr_days_night+nbr_days_extra), attributes='',
                                                      optional_product_ids=[ticket.product_id.id])
                SaleOrderLineSudo = request.env['sale.order.line'].sudo().browse([cart_values2['line_id']])
                SaleOrderLineSudo.write({'x_rental': True, 'x_start': event.date_begin + timedelta(days=nbr_days_extra_neg), 'x_end':event.date_end + timedelta(days=nbr_days_extra_pos), 'name': '%s\nEvent: %s day(s)\nExtra: %s day(s)\n' % (SaleOrderLineSudo.product_id.description_sale or SaleOrderLineSudo.product_id.name ,nbr_days_night, nbr_days_extra)})

            if nbr_days_extra and extra_rooms:
                for extra_product in extra_meals:
                    product = request.env['product.product'].browse(extra_product)
                    #cart_values2 = order._cart_update(product_id=product.id, linked_line_id=cart_values["line_id"],
                    #                                  add_qty=capacity*1, attributes='',
                    #                                  optional_product_ids=[ticket.product_id.id])
                    SaleOrderLineSudo = request.env['sale.order.line'].sudo().browse([cart_values2['line_id']])
                    #if extra_product == request.env.ref("website_booking.product_lunch").id:
                    #    SaleOrderLineSudo.write({'name': '%s\nExtra night: %s day(s)\n' % (
                    #                             SaleOrderLineSudo.product_id.description_sale or SaleOrderLineSudo.product_id.name,
                    #                             nbr_days_extra)})
                    #else:
                    cart_values2 = order._cart_update(product_id=product.id, linked_line_id=cart_values["line_id"],
                                                      add_qty=capacity,
                                                      attributes='',
                                                      optional_product_ids=[ticket.product_id.id])
                    SaleOrderLineSudo = request.env['sale.order.line'].sudo().browse([cart_values2['line_id']])
                    SaleOrderLineSudo.write(
                        {'x_rental': True, 'x_start': event.date_begin + timedelta(days=nbr_days_extra_neg),
                         'x_end': event.date_end + timedelta(days=nbr_days_extra_pos),
                         'name': '%s\nEvent: %s day(s)\nExtra: %s day(s)\n' % (
                         SaleOrderLineSudo.product_id.description_sale or SaleOrderLineSudo.product_id.name,
                         nbr_days_night, nbr_days_extra)})

                    #SaleOrderLineSudo.write(
                    #        {'name': '%s\nEvent night: %s day(s)\nExtra night: %s day(s)\n' % (
                    #            SaleOrderLineSudo.product_id.description_sale or SaleOrderLineSudo.product_id.name,
                    #            nbr_days_night, nbr_days_extra)})

            attendee_ids |= set(cart_values.get('attendee_ids', []))
        order.pricelist_id=order.partner_id.property_product_pricelist.id

        return request.redirect('/shop/cart')


        
    """    
    @http.route(['/event', '/event/page/<int:page>', '/events', '/events/page/<int:page>'], type='http', auth="public", website=True, sitemap=WebsiteEventController.sitemap_event)
    def events(self, page=1, **searches):
        Event = request.env['event.event']
        EventType = request.env['event.type']

        searches.setdefault('date', 'all')
        searches.setdefault('type', 'all')
        searches.setdefault('country', 'all')

        domain_search = {}

        def sdn(date):
            return fields.Datetime.to_string(date.replace(hour=23, minute=59, second=59))

        def sd(date):
            return fields.Datetime.to_string(date)
        today = datetime.today()
        dates = [
            ['all', _('Next Events'), [("date_end", ">", sd(today))], 0],
            ['today', _('Today'), [
                ("date_end", ">", sd(today)),
                ("date_begin", "<", sdn(today))],
                0],
            ['week', _('This Week'), [
                ("date_end", ">=", sd(today + relativedelta(days=-today.weekday()))),
                ("date_begin", "<", sdn(today + relativedelta(days=6-today.weekday())))],
                0],
            ['nextweek', _('Next Week'), [
                ("date_end", ">=", sd(today + relativedelta(days=7-today.weekday()))),
                ("date_begin", "<", sdn(today + relativedelta(days=13-today.weekday())))],
                0],
            ['month', _('This month'), [
                ("date_end", ">=", sd(today.replace(day=1))),
                ("date_begin", "<", (today.replace(day=1) + relativedelta(months=1)).strftime('%Y-%m-%d 00:00:00'))],
                0],
            ['nextmonth', _('Next month'), [
                ("date_end", ">=", sd(today.replace(day=1) + relativedelta(months=1))),
                ("date_begin", "<", (today.replace(day=1) + relativedelta(months=2)).strftime('%Y-%m-%d 00:00:00'))],
                0],
            ['old', _('Old Events'), [
                ("date_end", "<", today.strftime('%Y-%m-%d 00:00:00'))],
                0],
        ]

        # search domains
        # TDE note: WTF ???
        current_date = None
        current_type = None
        current_country = None
        for date in dates:
            if searches["date"] == date[0]:
                domain_search["date"] = date[2]
                if date[0] != 'all':
                    current_date = date[1]
        if searches["type"] != 'all':
            current_type = EventType.browse(int(searches['type']))
            domain_search["type"] = [("event_type_id", "=", int(searches["type"]))]

        if searches["country"] != 'all' and searches["country"] != 'online':
            current_country = request.env['res.country'].browse(int(searches['country']))
            domain_search["country"] = ['|', ("country_id", "=", int(searches["country"])), ("country_id", "=", False)]
        elif searches["country"] == 'online':
            domain_search["country"] = [("country_id", "=", False)]

        def dom_without(without):
            domain = ['|', ('company_id', '=', False), ('company_id', '=', request.env.user.company_id.id),('state', "in", ['draft', 'confirm', 'done'])]
            for key, search in domain_search.items():
                if key != without:
                    domain += search
            return domain

        # count by domains without self search
        for date in dates:
            if date[0] != 'old':
                date[3] = Event.search_count(dom_without('date') + date[2])

        domain = dom_without('type')
        types = Event.read_group(domain, ["id", "event_type_id"], groupby=["event_type_id"], orderby="event_type_id")
        types.insert(0, {
            'event_type_id_count': sum([int(type['event_type_id_count']) for type in types]),
            'event_type_id': ("all", _("All Categories"))
        })

        domain = dom_without('country')
        countries = Event.read_group(domain, ["id", "country_id"], groupby="country_id", orderby="country_id")
        countries.insert(0, {
            'country_id_count': sum([int(country['country_id_count']) for country in countries]),
            'country_id': ("all", _("All Countries"))
        })
    
        step = 10  # Number of events per page
        event_count = Event.search_count(dom_without("none"))
        pager = request.website.pager(
            url="/event",
            url_args={'date': searches.get('date'), 'type': searches.get('type'), 'country': searches.get('country')},
            total=event_count,
            page=page,
            step=step,
            scope=5)

        order = 'website_published desc, date_begin'
        if searches.get('date', 'all') == 'old':
            order = 'website_published desc, date_begin desc'
        events = Event.search(dom_without("none"), limit=step, offset=pager['offset'], order=order)

        values = {
            'current_date': current_date,
            'current_country': current_country,
            'current_type': current_type,
            'event_ids': events,  # event_ids used in website_event_track so we keep name as it is
            'dates': dates,
            'types': types,
            'countries': countries,
            'pager': pager,
            'searches': searches,
            'search_path': "?%s" % werkzeug.url_encode(searches),
        }

        return request.render("website_event.index", values)
    """


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
        partner=request.env["res.partner"].sudo().search([('barcode','=',reg.x_barcode)]) or request.env["res.partner"].sudo().search([('email','=',reg.email)])
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


    @http.route(['/check_page/partner/<string:begin>/<string:end>/<int:event_id>/<int:register_order_id>'], type='http', auth="user", website=True)
    def register_attend(self,begin,end,event_id,register_order_id):
        if register_order_id:
            request.env['event.registration'].browse([register_order_id]).write({'state':'done'})
            #pdf, _ = request.env.ref('sale.action_report_saleorder').sudo().render_qweb_pdf([sale_order_id])
            #pdfhttpheaders = [('Content-Type', 'application/pdf'), ('Content-Length', u'%s' % len(pdf))]
            #return request.make_response(pdf, headers=pdfhttpheaders)
        return request.redirect('/check_page/%s/%s/%s#%s'% (begin,end,event_id,register_order_id))

    @http.route(['/check_page/print/<int:sale_order_id>'], type='http', auth="user", website=True)
    def print_saleorder(self,sale_order_id):
        if sale_order_id:
            pdf, _ = request.env.ref('sale.action_report_saleorder').sudo().render_qweb_pdf([sale_order_id])
            pdfhttpheaders = [('Content-Type', 'application/pdf'), ('Content-Length', u'%s' % len(pdf))]
            return request.make_response(pdf, headers=pdfhttpheaders)
        else:
            return request.redirect('/check_page')

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


    @http.route(['/shop/direction/<int:event_id>'], type='http', auth="public", website=True)
    def direction(self,event_id):
        if event_id:
            event=request.env["event.event"].sudo().browse([event_id])
            values = {
                        'event':event,
                }
            return request.render('website_booking.direction', values)
        return request.redirect('/shop')


    @http.route(['/shop/direction/<int:event_id>'], type='http', auth="public", website=True)
    def direction(self,event_id):
        if event_id:
            event=request.env["event.event"].sudo().browse([event_id])
            values = {
                        'event':event,
                }
            return request.render('website_booking.direction', values)
        return request.redirect('/shop')

class WebsiteSale_Rental(WebsiteSale):
    
    """
    def _get_search_domain(self, search, category, attrib_values):
        domain = request.website.sale_product_domain()
        domain += ['|', ('company_id', '=', False), ('company_id', '=', request.env.user.company_id.id)]
        if search:
            for srch in search.split(" "):
                domain += ['|', '|', '|', ('name', 'ilike', srch), ('description', 'ilike', srch),
                    ('description_sale', 'ilike', srch), ('product_variant_ids.default_code', 'ilike', srch)]

        if category:
            domain += [('public_categ_ids', 'child_of', int(category))]

        if attrib_values:
            attrib = None
            ids = []
            for value in attrib_values:
                if not attrib:
                    attrib = value[0]
                    ids.append(value[1])
                elif value[0] == attrib:
                    ids.append(value[1])
                else:
                    domain += [('attribute_line_ids.value_ids', 'in', ids)]
                    attrib = value[0]
                    ids = [value[1]]
            if attrib:
                domain += [('attribute_line_ids.value_ids', 'in', ids)]

        return domain
   """


    @http.route(['/shop/confirm_order'], type='http', auth="public", website=True, sitemap=False)
    def confirm_order(self, **post):
        order = request.website.sale_get_order()

        redirection = self.checkout_redirection(order)
        if redirection:
            return redirection

        order.onchange_partner_shipping_id()
        order.order_line._compute_tax_id()
        request.session['sale_last_order_id'] = order.id
        #request.website.sale_get_order(update_pricelist=True)
        extra_step = request.env.ref('website_sale.extra_info_option')
        if extra_step.sudo().active:
            return request.redirect("/shop/extra_info")

        return request.redirect("/shop/payment")

    @http.route([
        '/shop',
        '/shop/page/<int:page>',
        '/shop/category/<model("product.public.category"):category>',
        '/shop/category/<model("product.public.category"):category>/page/<int:page>'
    ], type='http', auth="public", website=True)
    def shop(self, page=0, category=None, search='', ppg=False, **post):
        company_id = request.env["res.company"].search([('name','ilike','%TIBETAANS%')]).id
        if int(company_id) in request.env.user.company_ids.mapped("id"):
            request.env.user.company_id = company_id

        return super(WebsiteSale_Rental, self).shop(page,category,search,ppg,**post)
