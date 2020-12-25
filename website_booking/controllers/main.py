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


    @http.route(['/my/account/forget_me'], type='http', auth='user', website=True)
    def forget_me(self):
         #values = self._prepare_portal_layout_values()
        values={}
        return request.render("website_booking.forget_me", values)

    @http.route(['/my/account/forget_me_send'], type='http', auth='user', website=True)
    def forget_me_send(self):
        partner=request.env.user.partner_id
        template = request.env.ref('website_booking.email_template_forget_me')
        template.send_mail(partner.id)
        return request.render("website_booking.forget_me_send", {})

class WebsiteEventSaleController(WebsiteEventController):

    def _get_number_of_days(self, date_from, date_to):
        DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
        from_dt = datetime.strptime(date_from, DATETIME_FORMAT)
        to_dt = datetime.strptime(date_to, DATETIME_FORMAT)
        timedelta = to_dt - from_dt
        diff_day = timedelta.days + float(timedelta.seconds) / 86400
        return diff_day

    """
    @http.route(['/event/choice'], type='http', auth="public", methods=['GET'], website=True)
    def event_choice(self, id):
        if id :
            event=request.env["event.event"].sudo().browse([int(id)])
            if event:
                if event.company_id in request.env.user.company_ids:
                    request.env.user.company_id=event.company_id
                    return request.redirect(event.website_url)
        return redirect("/")

    """

    @http.route(['/event/<model("event.event"):event>/registration/error/<int:error_number>'], type='http', auth="public", website=True)
    def registration_error(self, event,error_number):
        if error_number==1:
           error=_("Only one registration per person is allowed !")
        if error_number==2:
            error=_("Sorry, there is no more room available in this room category.")
        data = {"event": event, "error":error}
        return request.render("website_booking.error", data)

    @http.route(['/event/<model("event.event"):event>/registration/confirm'], type='http', auth="public", methods=['POST'], website=True)
    def registration_confirm(self, event, **post):
        #clean order
        order = request.website.sale_get_order()
        request.website.sale_reset()
        if order:
            order.sudo().unlink()
        request.env.user.company_id = int(event.company_id)
        order = request.website.sale_get_order(force_create=1)
        DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
        DATE_FORMAT = "%Y-%m-%d"
        attendee_ids = set()
        registrations = self._process_registration_details(post)
        barcode_list=[]

        for registration in registrations:
            if registrations.count(registration)>1 :
                return request.redirect('/event/%s/registration/error/1' % slug(event))

        for registration in registrations:
            #pour chaque enregistrement
            # update ajouter l'adresse email
            # le nom, le phone
            # et sauver le barcode dans un champ pour la liste de prix
            registration["barcode"] = registration["name"]
            partner_price = request.env["res.partner"].sudo().search([('barcode', '=', registration['barcode'])])
            registration["name"] = partner_price[0].name
            registration["phone"] = partner_price[0].phone
            registration["email"] = partner_price[0].email
            #'email': 'fabian.monoyer@gmail.com',
            #'answer_ids-1': '2',
            #'phone': '494373920',
            #'ticket_id': '4',
            #'name': 'Monoyer Fabian',
            #'answer_ids': [[4, 2], [4, 4]],
            #'answer_ids-2': '4'}
            #pour chaque personne
            #nombre de jour d'event
            nbr_days_events = int(self._get_number_of_days(event.date_begin, event.date_end) + 1)
            #nombre de nuits par défaut
            nbr_days_night = int(self._get_number_of_days(event.date_begin, event.date_end))
            nbr_days_extra=0
            nbr_days_extra_neg=0
            nbr_days_extra_pos=0
            rooms=[]
            search_room=False
            extra_negatif=[]
            extra_positif=[]
            extra = []
            for key, value in registration.items():
                if key.find('answer_ids-')>=0:
                    answer = request.env["event.answer"].browse(int(value))
                    #ajoute les nuits supplémentaires, en cas de logement...
                    nbr_days_extra += abs(answer.x_days)

                    if answer.x_product_ids and answer.x_days==0 :
                        #ajoute les produits extra
                        extra +=answer.x_product_ids.mapped("id")

                    if answer.x_product_ids and answer.x_days<0 :
                        #ajoute les produits extra
                        nbr_days_extra_neg-=1
                        extra_negatif +=answer.x_product_ids.mapped("id")

                    if answer.x_product_ids and answer.x_days>0 :
                        #ajoute les produits extra
                        nbr_days_extra_pos += 1
                        extra_positif +=answer.x_product_ids.mapped("id")

                    if answer.x_type_logement:
                        search_room=True
                        rooms=request.env["product.product"].search([('x_is_room','=',True),('public_categ_ids','in',[answer.x_type_logement.id])])
                        #rechercher d'un logement

            #Si y a une chambre
            #filtrer les chambres libres
            room_choice = []
            for room in rooms:
                # la chambre n'est plus disponible après une certaine date.
                # print (product.x_available_until)
                ok=True
                if room.x_available_until and event.date_end and event.date_end[0:10] > room.x_available_until:
                     ok=False
                if ok and event.date_begin and event.date_end:
                     booking = request.env['booking.config'].sudo().search([], limit=1)

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

            ticket = request.env['event.event.ticket'].sudo().browse(int(registration['ticket_id']))

            if partner_price and registration['barcode'] not in barcode_list:
                order.pricelist_id=partner_price[0].property_product_pricelist.id
                barcode_list.append(registration['barcode'])
            else:
                # la liste de prix par défaut !!!
                order.pricelist_id=request.env['product.pricelist'].sudo().search([],limit=1)

            if search_room and len(room_choice)==0:
                return request.redirect('/event/%s/registration/error/2' % slug(event))

            #ajouter la reservation de l'event + les repas lunch
            cart_values = order.with_context(event_ticket_id=ticket.id, fixed_price=True)._cart_update(product_id=ticket.product_id.id, add_qty=1, registration_data=[registration])
            for product in ticket.event_id.x_product:
                cart_values2 = order._cart_update(product_id=product.id, linked_line_id=cart_values["line_id"],
                                                  add_qty=nbr_days_events, attributes='',
                                                  optional_product_ids=[ticket.product_id.id])

                SaleOrderLineSudo = request.env['sale.order.line'].sudo().browse([cart_values2['line_id']])
                SaleOrderLineSudo.write({'name': '%s\nFor registration : %s' % (SaleOrderLineSudo.product_id.description_sale or SaleOrderLineSudo.product_id.name, registration['name'])})

                if partner_price:
                    SaleOrderLineSudo = request.env['sale.order.line'].sudo().browse([cart_values['line_id']])
                    SaleOrderLineSudo.write({'name': '%s -> %s' % (SaleOrderLineSudo.name, registration['name']),
                                             'x_pricelist_id': partner_price[0].property_product_pricelist.id})

            capacity=1
            if len(room_choice)>0:
                choice = random.randrange(0, len(room_choice), 1)
                capacity = room_choice[choice].x_capacity
                #ajoute la chambre
                cart_values2 = order._cart_update(product_id=room_choice[choice].id, linked_line_id=cart_values["line_id"],
                                                      add_qty=(nbr_days_night+nbr_days_extra), attributes='',
                                                      optional_product_ids=[ticket.product_id.id])
                SaleOrderLineSudo = request.env['sale.order.line'].sudo().browse([cart_values2['line_id']])
                SaleOrderLineSudo.write({'x_rental': True, 'x_start': start, 'x_end':end, 'name': '%s\nEvent: %s day(s)\nExtra: %s day(s)\nFor registration : %s' % (SaleOrderLineSudo.product_id.description_sale or SaleOrderLineSudo.product_id.name ,nbr_days_night, nbr_days_extra, registration['name'])})

                if partner_price:
                    SaleOrderLineSudo = request.env['sale.order.line'].sudo().browse([cart_values['line_id']])
                    SaleOrderLineSudo.write({'name': '%s -> %s' % (SaleOrderLineSudo.name, registration['name']),
                                                 'x_pricelist_id': partner_price[0].property_product_pricelist.id})

                for mandatory in room_choice[choice].x_mandatory_product_ids:
                    cart_values2 = order._cart_update(product_id=mandatory.x_product_id.id, linked_line_id=cart_values["line_id"],
                                                      add_qty=((nbr_days_night+nbr_days_extra)*capacity*mandatory.x_qty), attributes='',
                                                      optional_product_ids=[ticket.product_id.id])

                    SaleOrderLineSudo = request.env['sale.order.line'].sudo().browse([cart_values2['line_id']])
                    SaleOrderLineSudo.write({'name': '%s\nEvent: %s day(s)\nExtra: %s day(s)\nFor registration : %s' % (
                    SaleOrderLineSudo.product_id.description_sale or SaleOrderLineSudo.product_id.name,nbr_days_night, nbr_days_extra, registration['name'])})

                    if partner_price:
                        SaleOrderLineSudo = request.env['sale.order.line'].sudo().browse([cart_values['line_id']])
                        SaleOrderLineSudo.write({'name': '%s -> %s' % (SaleOrderLineSudo.name, registration['name']),
                                                 'x_pricelist_id': partner_price[0].property_product_pricelist.id})


            for extra_product in extra_negatif:
                product = request.env['product.product'].browse(extra_product)
                cart_values2 = order._cart_update(product_id=product.id, linked_line_id=cart_values["line_id"],
                                                      add_qty=1, attributes='',
                                                      optional_product_ids=[ticket.product_id.id])
                SaleOrderLineSudo = request.env['sale.order.line'].sudo().browse([cart_values2['line_id']])
                SaleOrderLineSudo.write({'name': '%s\nEXTRA MEAL\nFor registration : %s' % (SaleOrderLineSudo.product_id.description_sale or SaleOrderLineSudo.product_id.name , registration['name'])})
                if partner_price:
                    SaleOrderLineSudo = request.env['sale.order.line'].sudo().browse([cart_values['line_id']])
                    SaleOrderLineSudo.write({'name': '%s -> %s' % (SaleOrderLineSudo.name, registration['name']),
                                                 'x_pricelist_id': partner_price[0].property_product_pricelist.id})

            for extra_product in extra:
                product = request.env['product.product'].browse(extra_product)
                cart_values2 = order._cart_update(product_id=product.id, linked_line_id=cart_values["line_id"],
                                                  add_qty=1, attributes='',
                                                  optional_product_ids=[ticket.product_id.id])
                SaleOrderLineSudo = request.env['sale.order.line'].sudo().browse([cart_values2['line_id']])
                SaleOrderLineSudo.write({'name': '%s\nEXTRA MEAL\nFor registration : %s' % (
                    SaleOrderLineSudo.product_id.description_sale or SaleOrderLineSudo.product_id.name,
                    registration['name'])})
                if partner_price:
                    SaleOrderLineSudo = request.env['sale.order.line'].sudo().browse([cart_values['line_id']])
                    SaleOrderLineSudo.write({'name': '%s -> %s' % (SaleOrderLineSudo.name, registration['name']),
                                             'x_pricelist_id': partner_price[0].property_product_pricelist.id})

            for extra_product in extra_positif:
                product = request.env['product.product'].browse(extra_product)
                cart_values2 = order._cart_update(product_id=product.id, linked_line_id=cart_values["line_id"],
                                                      add_qty=1, attributes='',
                                                      optional_product_ids=[ticket.product_id.id])
                SaleOrderLineSudo = request.env['sale.order.line'].sudo().browse([cart_values2['line_id']])
                SaleOrderLineSudo.write({'name':'%s\nEXTRA MEAL\nFor registration : %s' % (SaleOrderLineSudo.product_id.description_sale or SaleOrderLineSudo.product_id.name , registration['name'])})
                if partner_price:
                    SaleOrderLineSudo = request.env['sale.order.line'].sudo().browse([cart_values['line_id']])
                    SaleOrderLineSudo.write({'name': '%s -> %s' % (SaleOrderLineSudo.name, registration['name']),
                                                 'x_pricelist_id': partner_price[0].property_product_pricelist.id})


            attendee_ids |= set(cart_values.get('attendee_ids', []))
        order.pricelist_id=order.partner_id.property_product_pricelist.id
        return request.redirect('/shop/cart')

        #request.session['booking_mindate'] ='%s' % (event.date_begin[0:10])
        #request.session['booking_maxdate'] = '%s' %(event.date_end[0:10])
        #return request.redirect('/shop/booking?start=%s&end=%s&redirection=%s' % (event.date_begin,event.date_end,redirection))
        
        
        
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

    def _get_number_of_days(self, date_from, date_to):
        DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
        from_dt = datetime.strptime(date_from, DATETIME_FORMAT)
        to_dt = datetime.strptime(date_to, DATETIME_FORMAT)
        timedelta = to_dt - from_dt
        diff_day = timedelta.days + float(timedelta.seconds) / 86400
        return diff_day



    @http.route(['/shop/confirm_order'], type='http', auth="public", website=True)
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
        if extra_step.active:
            return request.redirect("/shop/extra_info")

        return request.redirect("/shop/payment")


    #verify if range special for booking
    @http.route(['/shop/booking/verify'], type='json', auth="public", website=True)
    def get_verify(self,start,end):
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry
        booking = request.env['booking.config'].sudo().search([],limit=1)
        tzuser = http.request.env.user.partner_id.tz or booking.tz
        start = datetime.strptime(start,"%Y-%m-%d %H:%M:%S")
        end = datetime.strptime(end, "%Y-%m-%d %H:%M:%S")
        start = start.replace(tzinfo=tz.gettz(tzuser))
        end = end.replace(tzinfo=tz.gettz(tzuser))
        start = start.astimezone(tz.gettz("UTC")).strftime("%Y-%m-%d %H:%M:%S")
        end = end.astimezone(tz.gettz("UTC")).strftime("%Y-%m-%d %H:%M:%S")
        bookdate = request.env['booking.date'].sudo().search([('dateStart','=',start),('dateStop','=',end),('config_id',"=",booking.id)], limit=1)
        if bookdate:
            return json.dumps({'result':True})
        return json.dumps({'result':False})


    #choice and return pricelist
    @http.route(['/shop/booking/config'], type='json', auth="public", website=True)
    def get_config(self):
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry
        booking = request.env['booking.config'].sudo().search([], limit=1)
        DATETIME_FORMAT = booking.date(False)
        daterange={}
        tzuser = http.request.env.user.partner_id.tz or booking.tz
        #for drange in booking.dateRange.search([('config_id','=',booking.id),("type","=","range")]):
        #    start=datetime.strptime(drange.dateStart, "%Y-%m-%d %H:%M:%S")
        #    end=datetime.strptime(drange.dateStop, "%Y-%m-%d %H:%M:%S")
        #    start = start.replace(tzinfo=tz.gettz("UTC"))
        #    end = end.replace(tzinfo=tz.gettz("UTC"))
        #    start = start.astimezone(tz.gettz(tzuser)).strftime("%Y-%m-%d %H:%M:%S")
        #    end = end.astimezone(tz.gettz(tzuser)).strftime("%Y-%m-%d %H:%M:%S")
        #    daterange.update({drange.name: ['%s' % (start),'%s' % (end)]})
        highSeason=[]
        averageSeason=[]
        lowSeason = []
        deactive = []

        #for drange in booking.dateRange.search([('config_id', '=', booking.id), ("type", "=", "deactivate")]):
        #    start = datetime.strptime(drange.dateStart[0:10], "%Y-%m-%d")
        #    end = datetime.strptime(drange.dateStop[0:10], "%Y-%m-%d")
        #    diff = abs((end - start).days)
        #    for x in range(0, diff + 1):
        #        deactive.append((start + datetime.timedelta(days=x)).strftime("%Y-%m-%d"))

        #for item in http.request.env['product.pricelist'].search([('x_rental','=',True)]):
        #    if item.x_start and item.x_end:
        #       start=datetime.strptime(item.x_start, "%Y-%m-%d")
        #       end = datetime.strptime(item.x_end, "%Y-%m-%d")
        #       diff=abs((end - start).days)
        #       for x in range(0, diff+1):
        #           if item.x_type=="high":
        #               highSeason.append((start + datetime.timedelta(days=x)).strftime("%Y-%m-%d"))
        #           if item.x_type=="average":
        #               averageSeason.append((start + datetime.timedelta(days=x)).strftime("%Y-%m-%d"))
        #           if item.x_type == "low":
        #              lowSeason.append((start + datetime.timedelta(days=x)).strftime("%Y-%m-%d"))

        locale = {
            'customRangeLabel':booking.customRangeLabel,
            "direction": booking.direction,
            "format": booking.format,
            "separator": booking.separator,
            "applyLabel": booking.applyLabel,
            "cancelLabel": booking.cancelLabel,
            "fromLabel": booking.fromLabel,
            "toLabel": booking.toLabel,
            "opens": "center",
        }

        from_dt = datetime.strptime(request.session['booking_mindate'], DATETIME_FORMAT[0:8])
        to_dt = datetime.strptime(request.session['booking_maxdate'], DATETIME_FORMAT[0:8])
        #if int(booking.day)>=0:
        #    minj=(date.today()+timedelta(days=booking.minDate)).weekday()
        #    maxj=(date.today()+dtimedelta(days=booking.maxDate)).weekday()
        #    diffminj=minj-int(booking.day)
        #    diffmaxj=maxj-int(booking.day)
        #    diffminj = diffminj * -1
        #    diffmaxj = diffmaxj * -1
        #    minDate = (date.today() +timedelta(days=2*booking.minDate)+timedelta(days=diffminj)).strftime(DATETIME_FORMAT)
        #    maxDate = (date.today() +timedelta(days=booking.maxDate)+timedelta(days=diffmaxj)).strftime(DATETIME_FORMAT)
        #else:
        #    minDate = (date.today() +timedelta(days=booking.minDate)).strftime(DATETIME_FORMAT)
        #    maxDate =(date.today() + timedelta(days=booking.maxDate)).strftime(DATETIME_FORMAT)

        minDate =(from_dt+timedelta(days=-1)).strftime(DATETIME_FORMAT)
        maxDate =(to_dt+timedelta(days=+1)).strftime(DATETIME_FORMAT)
        startDate = minDate
        endDate = startDate

        minDate = '%s %s' % (minDate,booking.defaultTimeTo)
        maxDate = '%s %s' % (maxDate,booking.defaultTimeFrom)
        startDate='%s %s' %(startDate,booking.defaultTimeTo)
        endDate='%s %s' %(endDate,booking.defaultTimeFrom)
        datalocal={
                "lang":context.get('lang','en_US').split("_")[0],
                "timePicker": booking.timePicker,
                "showWeekNumbers": booking.showWeekNumbers,
                "autoUpdateInput": booking.autoUpdateInput,
                "timePicker24Hour": True,
                "defaultTimeFrom":booking.defaultTimeFrom,
                "defaultTimeTo":booking.defaultTimeTo,
                "multiple":booking.multiple,
                "day": booking.day,
                "bsminDay": booking.bsminDay,
                "avminDay": booking.avminDay,
                "hsminDay": booking.hsminDay,
                "startDate": startDate,
                "endDate":  endDate,
                "minDate":  minDate,
                "maxDate":  maxDate,
                "ranges": daterange,
                "highSeason": highSeason,
                "averageSeason": averageSeason,
                "lowSeason": lowSeason,
                "dateDesactive":deactive,
                "locale":locale,
            }

        return json.dumps(datalocal)


    #choice and
    @http.route(['/shop/booking'], type='http', auth="public", website=True)
    def get_reservation_product(self, start, end, redirection):
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry
        booking = request.env['booking.config'].sudo().search([], limit=1)
        request.session['booking_start'] ='%s %s' % (start[0:10],booking.defaultTimeFrom)
        request.session['booking_end'] = '%s %s' %(end[0:10],booking.defaultTimeTo)

        order = request.website.sale_get_order(force_create=1)
        event_id=False
        for line in order.order_line:
            if line.linked_line_id.event_id :
                event_id=line.linked_line_id.event_id.id
                startok=start[0:10]
                endok=end[0:10]

                if startok<line.linked_line_id.event_id.date_begin:
                    startok=line.linked_line_id.event_id.date_begin[0:10]

                if endok>line.linked_line_id.event_id.date_end :
                    endok=line.linked_line_id.event_id.date_end[0:10]

                newqty=self._get_number_of_days('%s 12:00:00' % startok,'%s 12:00:00' % endok)+1
                if newqty>=0:
                    line.product_uom_qty=newqty
                    line.name="%s (%s - %s)" % (line.product_id.name,startok,endok)
                    if line.event_id :
                        line.name=line.product_id.name
        #if redirection and redirection!="True":
        #    return request.redirect('/web/login?redirect=%s'% redirection)
        if redirection!="False":
            return request.redirect('/web/login?redirect=/shop/direction/%s'%(event_id))
        return request.redirect('/shop/cart')


    """
    #add product
    @http.route()
    def cart_options_update_json(self, product_id, add_qty=1, set_qty=0, goto_shop=None, lang=None, **kw):
        DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
        if lang:
            request.website = request.website.with_context(lang=lang)

        order = request.website.sale_get_order(force_create=1)
        product = request.env['product.product'].browse(int(product_id))
        #si pas de produit dans le bon de commande
        #forcer la company_id avec celui de l'utilisateur
        if len(order.order_line.mapped("id"))==0 :
            order.company_id=request.env.user.company_id

        line_id=line_obli_id=None

        #convertir les quantités avec le factor qty
        if product.x_rental:
                from_dt = datetime.strptime(request.session['booking_start'][0:10], DATETIME_FORMAT[0:8])
                to_dt = datetime.strptime(request.session['booking_end'][0:10], DATETIME_FORMAT[0:8])
                timedelta = to_dt - from_dt
                seconds = float(timedelta.days * (24 * 60 * 60))
                if product.sudo().uom_id.factor_inv > 0:
                    set_qty = ((seconds + timedelta.seconds) / product.sudo().uom_id.factor_inv)
                else:
                    set_qty = (seconds + timedelta.seconds)
                add_qty = 0


        #liste des chambre déjà linkée a un event. il ne faudra pas les réutiliser
        notlink=[]
        for line in order.order_line:#si la chambre est linkée a un event.
           if line.product_id.x_is_room and line.linked_line_id.event_id :
               notlink.append(line.linked_line_id.id)

        for line in order.order_line:
                #Récupérer la ligne du produit
                if int(product_id)==line.product_id.id:
                    if not product.x_rental:
                        line_id=line.id
                if line.event_id and line.id not in notlink:
                    if line.x_pricelist_id:
                        order.pricelist_id=line.x_pricelist_id.id
                        #print("change pricelist")
                #Si on ajoute un produit chambre, on regarde pour le liée a un event
                #Verifier si une event est déjà linkée a une chambre
                #si oui ne pas linker une seconde.
                if product.x_is_room and line.event_id and line.id not in notlink:
                        date_ev_start=line.event_id.date_begin[0:10]
                        date_ev_end=line.event_id.date_end[0:10]
                        if product.x_is_room:
                            date_log_start=request.session['booking_start'][0:10]
                            date_log_end=request.session['booking_end'][0:10]
                            if (date_log_start<=date_ev_start) and (date_log_end>=date_ev_end) :
                               line_obli_id=line.id


        option_ids = product.optional_product_ids.mapped('product_variant_ids').ids
        optional_product_ids = []
        for k, v in kw.items():
            if "optional-product-" in k and int(kw.get(k.replace("product", "add"))) and int(v) in option_ids:
                optional_product_ids.append(int(v))

        attributes = self._filter_attributes(**kw)
        value = {}


        if not product.company_id or product.company_id==order.company_id:
            if add_qty or set_qty:
                if line_id:
                    value = order._cart_update(
                        product_id=int(product_id),
                        line_id=line_id,
                        linked_line_id=line_obli_id or None,
                        add_qty=int(add_qty),
                        set_qty=int(set_qty),
                        attributes=attributes,
                        optional_product_ids=optional_product_ids
                    )
                else:
                    value = order._cart_update(
                        product_id=int(product_id),
                        linked_line_id=line_obli_id or None,
                        add_qty=int(add_qty),
                        set_qty=int(set_qty),
                        attributes=attributes,
                        optional_product_ids=optional_product_ids
                    )

            # ajouter les dates de reservation pour le produit
            for line in order.order_line:
                if 'line_id' in value and line.id == value['line_id']:
                    if product.x_rental:
                        if not line.x_start or not line.x_end:
                            from_dt = datetime.strptime(request.session['booking_start'], DATETIME_FORMAT)
                            to_dt = datetime.strptime(request.session['booking_end'], DATETIME_FORMAT)
                            booking = request.env['booking.config'].sudo().search([],limit=1)
                            tzuser = http.request.env.user.partner_id.tz or booking.tz
                            start = from_dt.replace(tzinfo=tz.gettz(tzuser))
                            end = to_dt.replace(tzinfo=tz.gettz(tzuser))
                            start = start.astimezone(tz.gettz("UTC")).strftime(DATETIME_FORMAT)
                            end = end.astimezone(tz.gettz("UTC")).strftime(DATETIME_FORMAT)
                            line.x_start=start
                            line.x_end=end
                            line.x_rental=True

            #ajouter les produits en option
            for option_id in optional_product_ids:
                order._cart_update(
                    product_id=option_id,
                    set_qty=value.get('quantity'),
                    attributes=attributes,
                    linked_line_id=value.get('line_id')
                    )

            # check product mandatory (example : lunch, supper, breakfast,..)
            for mandatory in product.x_mandatory_product_ids:
                    #Ajoute les produits obligatoire (repas, draps,...)
                    #les lunchs sont spécifiques
                    #recherche les events inclus dans l'hébergement.
                    #faire la somme des lunch eventuelle selon le nombre de jours
                    if product.x_is_room:
                       multiplicateur=product.x_capacity
                    if  mandatory.x_type_qty=="multi-1": #lunch
                        #qty normal
                        qty=(mandatory.x_qty*(value.get('quantity',0.0)-1))*multiplicateur
                        countlunchevent=0
                        #compter les lunchs
                        for line in order.order_line:
                            #si l'event lié à notre produit.
                            if line_obli_id==line.id and line.event_id:
                                #qty des lunch de l'event
                                countlunchevent=self._get_number_of_days("%s 12:00:00"%line.event_id.date_begin[0:10],"%s 12:00:00"%line.event_id.date_end[0:10])+1
                        qty=qty-countlunchevent

                    #calculer le nombre de fois que le produit doit être ajouter
                    elif mandatory.x_type_qty=="oneshot": # les draps,..
                        qty=mandatory.x_qty*multiplicateur
                    elif mandatory.x_type_qty=="multi" : # ex breakfast,supper
                        qty=(mandatory.x_qty*value.get('quantity',0.0))*multiplicateur
                    if qty>0:
                        order._cart_update(
                        product_id=mandatory.x_product_id.id,
                        set_qty=qty,
                        attributes=attributes,
                        linked_line_id=value.get('line_id')
                        )
        #print("correction liste de prix")
        order.pricelist_id=order.partner_id.property_product_pricelist
        return str(order.cart_quantity)
        """

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
