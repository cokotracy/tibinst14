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
from odoo import models,fields,api
from odoo.tools import pycompat
from odoo.tools import float_compare
"""
class Mandatory(models.Model):
    _name="product.mandatory"

    name=fields.Char(string="name")
    x_product_id=fields.Many2one("product.product",string="Product")
    x_type_qty=fields.Selection([('oneshot','Oneshot'),('multi','* units'),('multi-1','*(units -1)')],string="Type")
    x_qty=fields.Float(string="Quantity")
"""
class Template(models.Model):
    _inherit="product.template"

    x_rental = fields.Boolean(string="Rental")
    x_is_room = fields.Boolean(string="Is Room")
    x_is_meal = fields.Boolean(string="Is Meal")
    x_removing_qty = fields.Boolean(string="Removing qantity on cart")
    #x_mandatory_product_ids = fields.Many2many('product.mandatory',string="Mandatory")
    x_capacity = fields.Integer(string="Capacity")
    x_planning_role_ids = fields.Many2many("planning.role",string="Room")

"""
class Category(models.Model):
    _inherit="product.public.category"

    x_rental = fields.Boolean(string="Visible if user add an event to cart")
"""

class ProductProduct(models.Model):
    _inherit ="product.product"

    def _website_price(self):
        qty = self._context.get('quantity', 1.0)
        partner = self.env.user.partner_id
        current_website = self.env['website'].get_current_website()
        pricelist = current_website.get_current_pricelist()
        company_id = self.env.user.company_id

        context = dict(self._context, pricelist=pricelist.id, partner=partner)
        self2 = self.with_context(context) if self._context != context else self

        ret = self.env.user.has_group('sale.group_show_price_subtotal') and 'total_excluded' or 'total_included'

        for p, p2 in pycompat.izip(self, self2):
            taxes = partner.property_account_position_id.map_tax(
                p.sudo().taxes_id.filtered(lambda x: x.company_id == company_id))
            p.website_price = \
            taxes.compute_all(p2.price, pricelist.currency_id, quantity=qty, product=p2, partner=partner)[ret]
            # We must convert the price_without_pricelist in the same currency than the
            # website_price, otherwise the comparison doesn't make sense. Moreover, we show a price
            # difference only if the website price is lower
            price_without_pricelist = p.list_price
            if company_id.currency_id != pricelist.currency_id:
                price_without_pricelist = company_id.currency_id.compute(price_without_pricelist, pricelist.currency_id)
            price_without_pricelist = taxes.compute_all(price_without_pricelist, pricelist.currency_id)[ret]
            p.website_price_difference = True if float_compare(price_without_pricelist, p.website_price,
                                                               precision_rounding=pricelist.currency_id.rounding) > 0 else False
            p.website_public_price = taxes.compute_all(p2.lst_price, quantity=qty, product=p2, partner=partner)[ret]
