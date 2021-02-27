# -*- coding: utf-8 -*-
# #Copyright (C) Monoyer Fabian (info@olabs.be)                                         #
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
from odoo import api, fields, models, tools, _
from datetime import date,timedelta
import logging
_logger = logging.getLogger(__name__)

DATETIME_FORMAT="%Y-%m-%d"

class Product(models.Model):
    _inherit = 'sale.subscription'

    """
    def _cron_membership_today(self):
        #Activer les liste de prix pour les membership en cours depuis 7 jours
        date_modif=(date.today()-timedelta(days=7)).strftime(DATETIME_FORMAT)
        nrecordall=self.env["sale.subscription"].search_count([('state','=','open'),('date_start','>',date_modif)])
        _logger.info("Count subscription for %s" % nrecordall)
        if nrecordall>0:
            recordall=self.env["sale.subscription"].search([('state','=','open'),('date_start','>',date_modif)])
            _logger.info("Count subscription for %s" % nrecordall)
            for record in recordall:
                _logger.info("Sale subscription for %s" % record.partner_id.name)
                for line in record.recurring_invoice_line_ids:
                    if line.product_id.x_pricelist_id: # le membre avec la nouvelle pricelist
                        _logger.info("Sale subscription update for %s" % record.partner_id.name)
                        record.partner_id.write({"property_product_pricelist":line.product_id.x_pricelist_id.id})

    """
    """
    def _cron_membership_clean(self):
        #nettoie les abonnements memberships expiré depuis hier     
        date_modif=(date.today()-timedelta(days=1)).strftime(DATETIME_FORMAT)
        #rechercher toute les subscriptions qui comporte des articles pour des memberships => retourne les id
        nrecordids=self.env["sale.subscription.line"].search([]).filtered(lambda l: l.product_id.x_pricelist_id != None).mapped('analytic_account_id.id')
        #filtrer seulement ceux qui sont pas en progress et dont la date de la dernière modification est supérieure à 1 jours.
        if nrecordids:
            nrecord=self.env["sale.subscription"].browse(nrecordids).filtered(lambda s: s.state in ['draft','renew','cancel','close'] and s.write_date > date_modif)
            #Remettre la liste de prix à zéro pour ceux-ci
            nrecord.partner_id.write({"property_product_pricelist":self.env["product.pricelist"].search([],limit=1)})
    """
