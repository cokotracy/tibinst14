# -*- coding: utf-8 -*-
from odoo import fields, http, _
from odoo.http import request
from odoo.addons.website_event.controllers.main import WebsiteEventController
from odoo.tools.misc import get_lang
import babel.dates

class TibinstWebsiteEventController(WebsiteEventController):

    def get_tibinst_formated_date(self, event):
        start_date = fields.Datetime.from_string(event.date_begin).date()
        end_date = fields.Datetime.from_string(event.date_end).date()
        month = babel.dates.get_month_names('abbreviated', locale=get_lang(event.env).code)[start_date.month]
        return ('%s,%s%s') % (month, start_date.strftime("%e"), (end_date != start_date and ("-" + end_date.strftime("%e")) or ""))

    @http.route('/event/get_country_event_list', type='json', auth='public', website=True)
    def get_country_events(self, **post):
        Event = request.env['event.event']
        country_code = request.session['geoip'].get('country_code')
        result = {'events': [], 'country': False}
        events = None

        if request.website.company_id.id != 1: # 1 = Umbrella
            domain = request.website.website_domain()
        else:
            domain = [('x_display_umbrella','=',True)]
        if country_code:
            country = request.env['res.country'].search([('code', '=', country_code)], limit=1)
            events = Event.search(domain + ['|', ('address_id', '=', None), ('country_id.code', '=', country_code), ('date_begin', '>=', '%s 00:00:00' % fields.Date.today())], order="date_begin")
        if not events:
            events = Event.search(domain + [('date_begin', '>=', '%s 00:00:00' % fields.Date.today())], order="date_begin")
        for event in events:
            event_date = self.get_tibinst_formated_date(event)
            if country_code and event.country_id.code == country_code:
                result['country'] = country
            result['events'].append({
                "month": event_date.split(',')[0],
                "day": event_date.split(',')[1],
                "event": event,
                "url": '%s%s' % (event.website_id.domain, event.website_url)})
        for web in request.env["website"].search([]):
            result.update({'url_comp_%s' % web.id: '%s%s' % (web.domain,'/event')})
            result.update({'name_comp_%s' % web.id: web.name})
        return request.env['ir.ui.view']._render_template("website_event.country_events_list", result)

