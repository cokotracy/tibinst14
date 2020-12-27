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
import datetime
import pytz
from dateutil import tz

from odoo.http import request
from odoo import api, models, fields, tools, _


class Website(models.Model):
    _inherit="website"


    def _prepare_sale_order_values(self, partner, pricelist):
        self.ensure_one()
        affiliate_id = request.session.get('affiliate_id')
        salesperson_id = affiliate_id if self.env['res.users'].sudo().browse(affiliate_id).exists() else request.website.salesperson_id.id
        addr = partner.address_get(['delivery', 'invoice'])
        default_user_id = partner.parent_id.user_id.id or partner.user_id.id
        values = {
            'partner_id': partner.id,
            'pricelist_id': pricelist.id,
            'payment_term_id': self.sale_get_payment_term(partner),
            'team_id': self.salesteam_id.id,
            'partner_invoice_id': addr['invoice'],
            'partner_shipping_id': addr['delivery'],
            'user_id': salesperson_id or self.salesperson_id.id or default_user_id,
            'company_id':request.env.user.company_id.id,
            'warehouse_id:':request.env['stock.warehouse'].sudo().search([("company_id","=",request.env.user.company_id.id)])[0]
        }
        return values

    def _if_user_public(self):
        if request.env.user==request.website.user_id:
            return True
        else :
            return False


    #vérifie la disponibilité des articles
    def _get_housing_free(self,event):
        nbr=nbr_total=0
        booking = request.env['booking.config'].sudo().search([],limit=1)
        products=self.env["product.product"].search([('x_is_room','=',True),('website_published','=',True)])
        nbr=nbr_total=len(products)
        for product in products:
            query= [("product_id.id","=",product.id),
                    ("x_start", "<=", '%s %s' %(str(event.date_end)[0:10],booking.defaultTimeTo)),
                    ("x_end", ">=",   '%s %s' %(str(event.date_begin)[0:10],booking.defaultTimeFrom)),
                    ('order_id.state', 'not in', ["cancel", "draft"])]

            order=self.env["sale.order.line"].sudo().search_count(query)
            if order>0:
                nbr-=order
        return '%s/%s'% (nbr,nbr_total)

    def _getdate_reservation(self):
        if 'booking_start' in request.session and 'booking_end' in request.session :
            return _('%s to %s') % (request.session['booking_start'][0:10],request.session['booking_end'][0:10])
        return None
        
    #Vérifie si le produit est une chambre et si le panier contient un événement.
    #Si pas ok, on bloque le panier.
    def _product_event(self,product):
	    if not product.x_is_room: # si pas une chambre, pas d'inquiétude
	    	return True
	    else:
			 #regarder si dans le panier il y a un événement, sinon il faut bloquer le panier.
			 #Normalement cela n'arrivera pas sauf si l'utilisateur supprime l'événement et retourne dans le webshop pour 
			 #louer une chambre
             order = request.website.sale_get_order()
             if order.mapped("order_line.event_id.id")==[]: 
              	return False
	    return True
	    
    #Vérifie si le produit est dans la meme company que la sale order
    def _product_company(self,product):
        order = request.website.sale_get_order()

        if order and len(order.mapped("order_line.id"))==0 :
            #force la company, utile si le bon de commande a été créer dans une autre.
            #Update 14 Mars 2019

            #si le produit contient une company, forcer le reste
            if product.company_id :
               order.company_id=product.company_id.id
               request.env.user.company_id=product.company_id.id
            else: #sinon le forcer avec la company du client
               order.company_id=request.env.user.company_id
               order.warehouse_id=request.env['stock.warehouse'].sudo().search([("company_id","=",request.env.user.company_id.id)])[0]

        #donc si pas de bon = OK
        #Si pas de company pour le produit OK
        #Si le produit dans la company de la vente OK       
        if not order or not product.company_id or (order and product.company_id==order.company_id):
            return True
        return False

    #Vérifie si un event est présent dans la saleorder
    def _sale_event(self,categ):
        if categ.x_rental:
            order = request.website.sale_get_order()
            event=order.mapped('order_line.event_id.id')
            if len(event)>0:
                return True
            return False
        return True

    #Vérifie si l'article est disponible à la réservation
    def _reservation(self, product=None,start=None,end=None,method=1):
        start=End=False
        DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"

        order = request.website.sale_get_order() # pas de sale order => l'utilisateur ne peux pas sélectionner une chambre
        if not order:
            return None

        if order.mapped("order_line.id")==[]: # pas de line order => l'utilisateur ne peux pas sélectionner une chambre
            return None

        if order.mapped("order_line.event_id.id")==[]: # pas de event order => l'utilisateur ne peux pas sélectionner une chambre
            return None

        if not start and not end and 'booking_start' in request.session and 'booking_end' in request.session :
            start=request.session['booking_start']
            end=request.session['booking_end']

        if not start or not end : # pas de date => l'utilisateur ne peux pas séléctionner une chambre
           return None

        if product and product.x_is_room:
            #La chambre est toujours libre pour les partenaires qui sont liés au produit.
            if self.env.user.partner_id in product.x_partner_ids:
                return True
            #la chambre n'est plus disponible après une certaine date.
            #print (product.x_available_until)
            if product.x_available_until and end and end[0:10]>product.x_available_until:
                return False

        if start and end:
                booking = request.env['booking.config'].sudo().search([],limit=1)
                from_dt = datetime.datetime.strptime(start, DATETIME_FORMAT)
                to_dt = datetime.datetime.strptime(end, DATETIME_FORMAT)
                tzuser = request.env.user.partner_id.tz or booking.tz
                start = from_dt.replace(tzinfo=tz.gettz(tzuser))
                end = to_dt.replace(tzinfo=tz.gettz(tzuser))
                start = start.astimezone(tz.gettz("UTC")).strftime(DATETIME_FORMAT)
                end = end.astimezone(tz.gettz("UTC")).strftime(DATETIME_FORMAT)

                now = datetime.datetime.now()
                now_minus_delay = str(now + datetime.timedelta(minutes = -booking.delay))

                order = request.website.sale_get_order()
                if method==1:
                    query= [("product_id.product_tmpl_id.id","=",product.id),
                    ("product_id.x_rental", "=", True),
                    ("x_start", "<=", str(end)), ("x_end", ">=",str(start)),
                    '|',
                    '&',('order_id.write_date', '>', now_minus_delay), ('order_id.state', '=', "draft"),
                    ('order_id.state', 'not in', ["cancel", "draft"])]

                if method==2:
                    query=[("product_id.product_tmpl_id.id","=",product.id),
                    ("product_id.x_rental", "=", True),
                    ("x_start", "<=", str(end)), ("x_end", ">=",str(start)),
                    '|',
                    '&','&',('order_id.write_date', '>', now_minus_delay),('order_id.id', '!=',order.id), ('order_id.state', '=', "draft"),
                    ('order_id.state', 'not in', ["cancel", "draft"])]

                orderline=self.env["sale.order.line"].sudo().search_count(query)
                if orderline>0:
                    return False
        else:
              return None
        return True
