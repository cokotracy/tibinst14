from odoo import http, fields, _, exceptions
from odoo.http import request
import werkzeug
from werkzeug.exceptions import NotFound
from datetime import datetime, timedelta

class KyglWebsiteDonation(http.Controller):

    @http.route(['/donation_page','/donation_page/<string:fond_select>'], auth='public', website=True)
    def donation_page(self, fond_select=False, **kwargs):
        countries =request.env['res.country'].sudo().search([])
        fond = request.env['product.product'].sudo().search([('product_tmpl_id.kygl_code', '=', '%s-U' % fond_select)])
        connection = False
        partner = False if request.env.user.id == request.env.ref('base.public_user').id else request.env.user.partner_id
        if not partner:
            connection = True
        values = {
             'connection': connection,
             'fond_select_data': fond,
             'fond_select': fond.kygl_code,
             'partner': "" if request.env.user.id == request.env.ref('base.public_user').id else request.env.user.partner_id,
             'countries': countries,
             'montants': request.env.ref('kygl_website_donation.kygl_amount_donation').sudo().value.split("-"),
         }

        return http.request.render('kygl_website_donation.donation_page', values)


    # Check and insert values from the form on the model <model>
    @http.route('/save_donation', type='http', auth="public", methods=['POST'], website=True)
    def save_donation(self, **kwargs):
        '''
        :param kwargs:
        fond=on
        &amount=30
        &amount_man=
        &type=U
        &email=welcome%40tibinst.org
        &name=Kagyu+Yeunten++Gyamtso+Ling
        &street=.strret
        &zip=.dddss
        &city=.ddd
        &country=20
        :return:
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
        fond_code = kwargs['fond_code'] if 'fond_code' in kwargs and kwargs['fond_code'] else ''
        type = kwargs['type'] if 'type' in kwargs and kwargs['type'] else ''
        receipt = 'annual'
        product = request.env["product.product"].sudo().search([('product_tmpl_id.kygl_code', '=', '%s-%s' % (fond_code.split("-")[0],type))])
        price = float(kwargs['amount_man']) if 'amount_man' in kwargs and kwargs['amount_man'] else 0.0
        if float(price) == 0.0:
            price = float(kwargs['amount']) if 'amount' in kwargs and kwargs['amount'] else 0.0

        #create SO
        #company_id = request.env["res.company"].search([('name','ilike','%TIBETAANS%')]).id
        #if int(company_id) in request.env.user.company_ids.mapped("id"):
        #    request.env.user.company = company_id
        order = request.website.sale_get_order()
        if order:
            request.website.sale_reset()
            order.order_line.unlink()
            order.unlink()
        order = request.website.sale_get_order(force_create=1)
        data = {
                'partner_id': partner.id,
                'message_donation': message,
                'tax_receipt_option': receipt,
                'partner_invoice_id':partner.id,
                'partner_shipping_id':partner.id,
                'order_line': [(0, 0, {'name': 'donation : %s ' % product.name,
                                   'product_id': product.id,
                                   'product_uom_qty': 1,
                                   'price_unit': price})]}

        order.sudo().write(data)
        order.sudo().onchange_partner_id()
        order.sudo().onchange_partner_shipping_id()  # fiscal position
        order.sudo().payment_term_id = request.website.sale_get_payment_term(partner)
        order.sudo().order_line._compute_tax_id()
        order.sudo().write({'tax_receipt_option': receipt})
        partner.sudo().write({'last_website_so_id': order.id})
        request.session['sale_order_id'] = order.id
        request.session['sale_last_order_id'] = order.id

        return request.redirect("/shop/payment")
