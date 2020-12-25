# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request
import json
from datetime import datetime

class WebsiteCalendarBlock(http.Controller):


    @http.route(['/choice/is_instituut/<company>'],type='http',auth='public',website=True)
    def _is_company_select(self,company):
       
            if company=="OTHERS" and (request.session.get('center_other',False)==True):
                return json.dumps({'result': 1})
            
            if request.session.get('center_other',False)==False and request.env.user.company_id.company_registry==str(company[1:]).replace("_","."):
                return json.dumps({'result': 1})
            else :
                return json.dumps({'result': 0})
             
    @http.route(['/choice/instituut/<company>'],type='http',auth='public',website=True)
    def set_choice(self, company,**post):
        cr, uid, context = request.cr, request.uid, request.context
        resultat="OK"
        message=""
        result=request.env['res.company'].sudo().search([('company_registry','=',str(company).replace("L","").replace("_","."))])
        if result:
                request.session['center_other']=False   # pas les centres partenaires pour le calendrier
                if result[0].id in request.env.user.company_ids.mapped("id"):
                    request.env.user.company_id=int(result[0].id)
                    resultat="OK"
        else:
            if company=="OTHERS": # le centre partenaire pour le calendrier
                request.session['center_other']=True    
                resultat="OK"
            else:
                resultat="ERROR"
                message="Company error"
        return json.dumps({'result': resultat, 'message': message})

        #return json.dumps({'result': "ok", 'message': ''})


    @http.route(['/calendar_block/get_events/<int:start>/<int:end>'],type='http',auth='public',website=True)
    def get_events(self, start, end, **post):
        cr, uid, context = request.cr, request.uid, request.context

        # Get events
        calendar_event_obj = request.env['event.event']
        condition=(('date_begin', '<', str(datetime.fromtimestamp(end))),('date_end', '>', str(datetime.fromtimestamp(start))),('state', 'not in', ['draft','cancel']),('website_published','=',True))
        #regarde si sélection des autres centres qui ne sont pas des sociétés
        #ce paramaètre des dans une variable de session
        #if request.session.get('center_other',False) == True : 
        #     condition=(*condition,('company_id', '=', False))
        #else: 
        #     condition=(*condition,('company_id', 'child_of', [request.env.user.company_id.id]))
        calendar_events = calendar_event_obj.sudo().search(list(condition))
        # Events
        events = []
        for calendar_event in calendar_events:
            # Fetch attendees
            attendees = []
            attendees.append({'id': calendar_event.organizer_id.id,'name': calendar_event.organizer_id.name})

            events.append(
                {'id': calendar_event.id,
                 'start': calendar_event.date_begin,
                 'end': calendar_event.date_end,
                 'title': calendar_event.name,
                 'color': calendar_event.color,
                 'url': calendar_event.website_url,
                 'attendees': attendees,
                 'allDay':False,
                 })

        return json.dumps({'events': events, 'contacts': ''})
