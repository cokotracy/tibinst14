#-*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
from odoo import api, fields, models, tools
from odoo.http import request

_logger = logging.getLogger(__name__)

class Website(models.Model):
    _inherit = 'website'


    def sale_get_order(self, force_create=False, code=None, update_pricelist=False, force_pricelist=False):
            saleOrder=super(Website,self).sale_get_order(force_create,code,update_pricelist,force_pricelist)
            if saleOrder:
                saleOrder.donation_sale_change()
            return saleOrder
