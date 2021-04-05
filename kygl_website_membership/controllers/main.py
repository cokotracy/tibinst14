from odoo import http, fields, _, exceptions
from odoo.http import request
import werkzeug
from werkzeug.exceptions import NotFound
from datetime import datetime, timedelta

class KyglWebsiteMembershio(http.Controller):

    @http.route(['/membership_page_nl/<string:membership_select>','/membership_page_fr/<string:membership_select>'], auth='public', website=True)
    def membership_page(self, membership_select=False, **kwargs):
        countries =request.env['res.country'].sudo().search([])
        membership_u = request.env['product.product'].sudo().search([('product_tmpl_id.kygl_code', '=','%s-U' % membership_select)])
        membership_m = request.env['product.product'].sudo().search([('product_tmpl_id.kygl_code', '=','%s-M' % membership_select)])
        membership_y = request.env['product.product'].sudo().search([('product_tmpl_id.kygl_code', '=','%s-Y' % membership_select)])
        membership_select = membership_u.product_tmpl_id.kygl_code
        connection = False
        partner = False if request.env.user.id == request.env.ref('base.public_user').id else request.env.user.partner_id
        if not partner:
            connection = True

        values = {
             'connection': connection,
             'membership_select_data': membership_u,
             'membership_select': membership_select,
             'partner': "" if request.env.user.id == request.env.ref('base.public_user').id else request.env.user.partner_id,
             'countries': countries,
             'amount_u': membership_u.list_price,
             'amount_m': membership_m.list_price,
             'amount_y': membership_y.list_price,
        }

        if request.context.get("lang",False) == "fr_BE":
            return http.request.render('kygl_website_membership.membership_page_nl', values)
        else:
            return http.request.render('kygl_website_membership.membership_page_fr', values)


    # Check and insert values from the form on the model <model>
    @http.route('/save_membership', type='http', auth="public", methods=['POST'], website=True)
    def save_donation(self, **kwargs):
        '''
        :param kwargs:
        '''
        iamcompany = kwargs['iamcompany'] if 'iamcompany' in kwargs and kwargs['iamcompany'] else 0
        email = kwargs['email'] if 'email' in kwargs and kwargs['email'] else ''
        message = kwargs['message'] if 'message' in kwargs and kwargs['message'] else ''
        company_data = {
            'name': kwargs['company'] if 'company' in kwargs and kwargs['company'] else '',
            'vat': kwargs['vat'] if 'vat' in kwargs and kwargs['vat'] else '',
            'email': email,
            'street': kwargs['street'] if 'street' in kwargs and kwargs['street']  else '',
            'city': kwargs['city'] if 'city' in kwargs and kwargs['city']  else '',
            'zip': kwargs['zip'] if 'zip' in kwargs and kwargs['zip']  else '',
            'phone': kwargs['phone'] if 'phone' in kwargs and kwargs['phone']  else '',
            'country_id': int(kwargs['country_id']) if 'country_id' in kwargs and kwargs['country_id'] else '' ,
            'company_type': 'company',
        }
        data = {
            'name': kwargs['name'] if 'name' in kwargs and kwargs['name']  else '',
            'email': email,
            'street': kwargs['street'] if 'street' in kwargs and kwargs['street']  else '',
            'city': kwargs['city'] if 'city' in kwargs and kwargs['city']  else '',
            'zip': kwargs['zip'] if 'zip' in kwargs and kwargs['zip']  else '',
            'country_id': int(kwargs['country_id']) if 'country_id' in kwargs and kwargs['country_id']  else '',
            'phone': kwargs['phone'] if 'phone' in kwargs and kwargs['phone'] else '',
        }

        partner = False if request.env.user.id == request.env.ref('base.public_user').id else request.env.user.partner_id
        if not partner:
            if iamcompany == 'on':
                #create company
                company = request.env['res.partner'].sudo().create(company_data)
                data.update({'parent_id':company.id})
            partner = request.env['res.partner'].sudo().create(data)
        else:
            partner.sudo().write(data)

        #search product
        membership_code = kwargs['membership_code'] if 'membership_code' in kwargs and kwargs['membership_code'] else ''
        type = kwargs['type'] if 'type' in kwargs and kwargs['type'] else ''
        product = request.env["product.product"].sudo().search([('product_tmpl_id.kygl_code', '=', '%s-%s' % (membership_code.split("-")[0],type))])
        price = product.list_price

        order = request.website.sale_get_order()
        if order:
            request.website.sale_reset()
            order.order_line.unlink()
            order.unlink()
        order = request.website.sale_get_order(force_create=1)
        data = {
                'partner_id': partner.id,
                'partner_invoice_id': partner.id,
                'partner_shipping_id': partner.id,
                'order_line': [(0, 0, {'name': 'Membership : %s ' % product.name,
                                   'product_id': product.id,
                                   'product_uom_qty': 1,
                                   'price_unit': price})]}

        order.sudo().write(data)
        order.sudo().onchange_partner_id()
        order.sudo().onchange_partner_shipping_id()  # fiscal position
        order.sudo().payment_term_id = request.website.sale_get_payment_term(partner)
        order.sudo().order_line._compute_tax_id()
        partner.sudo().write({'last_website_so_id': order.id})
        request.session['sale_order_id'] = order.id
        request.session['sale_last_order_id'] = order.id

        return request.redirect("/shop/payment")
