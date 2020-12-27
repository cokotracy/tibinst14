# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale

class WebsiteSale_option(WebsiteSale):

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
        if extra_step.active and order._message_wall():
            return request.redirect("/shop/extra_info")

        return request.redirect("/shop/payment")



