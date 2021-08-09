#!/usr/bin/env click-odoo
from __future__ import print_function
import sys
import logging
import datetime
from datetime import timedelta
import xmlrpc.client

logging.info('Opening Odoo session')
#workbook = xlrd.open_workbook((sys.argv[1]))
#worksheet = workbook.sheet_by_index(0)
#f = open((sys.argv[1]), 'r', encoding='utf-8')
# 0 Code Barre
# 1 Liste de prix de vente/Nom de la liste de prix
# 2 Nom
# 3 type
# 4 Date de début
# 5 Date de la prochaine facture
# 6 Lignes de facture/Nom à afficher
partner_model = env['res.partner']
journal_model = env['account.journal']
move_model = env['account.move']
so_model = env['sale.order']
prod_model = env['product.product']
membership_model = env['membership.membership_line']
subscription_model = env['sale.subscription.line']

url = "http://127.0.0.1:11000"
base = "tibinst11"
username = "fmo@olabs.be"
password = "fmocheepee7"
common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
print(common.version())

mod = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
uid = common.authenticate(base, username, password, {})
models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
partners = models.execute_kw(base, uid, password, 'res.partner', 'search_read',[[['customer','=',True]]], {'fields': ['id', 'name']})
sale_lines = models.execute_kw(base, uid, password, 'sale.subscription.line', 'search_read',
                              [[['name', 'ilike', 'member']]], {'fields': ['id', 'name', 'price_unit','analytic_account_id']})
sale_ids = [s['analytic_account_id'][0] if s['analytic_account_id'] else 0 for s in sale_lines]
lines = []
for partner in partners:
    external = models.execute_kw(base, uid, password, 'ir.model.data', 'search_read', [[['model','=','res.partner'],['res_id','=',partner['id']]]], {'fields': ['id', 'name']})
    if external:
        external_id = external[0]['name']
        sales = models.execute_kw(base, uid, password, 'sale.subscription', 'search_read',
                                 [[['partner_id','=',partner['id']],['id','in',sale_ids]]], {'fields': ['id', 'code', 'state', 'partner_id', 'date_start', 'date', 'recurring_next_date', 'recurring_total']})
        for sale in sales:
            line = models.execute_kw(base, uid, password, 'sale.subscription.line', 'search_read',
                                     [[['analytic_account_id', 'in', [sale['id']]]]], {
                                         'fields': ['id', 'name', 'price_unit', 'product_id', 'analytic_account_id']})
            lines.append(
                [external_id,
                 line[0]['product_id'][1],
                 sale['date_start'],
                 sale['recurring_next_date']
            ])

i = 0
journal = journal_model.search([('id','=',1)])

for line in lines:
    if i > 0 and len(line) > 1:
        try:
            partref = line[0]
            name = line[1]
            type='U'
            type2='M'
            date_start = line[2]
            date_end = line[3]

            partner = env.ref('__export__.%s' % partref)

            if name.lower().find("year") > -1:
                type ='A'
            if name.lower().find("month") > -1:
                type ='M'
            if name.lower().find('honorary') > -1:
                type2='H'
            if name.lower().find('supporting') > -1:
                type2='S'
            print("%s %s %s " %(name,type,type2))
        except:
            partner = False

        #Honorary
        HM = env.ref('kygl_website_membership.kygl_product_m3_m')
        HU = env.ref('kygl_website_membership.kygl_product_m3_u')
        HY = env.ref('kygl_website_membership.kygl_product_m3_y')
        #Standard - Unique
        UM = env.ref('kygl_website_membership.kygl_product_m1_m')
        UU = env.ref('kygl_website_membership.kygl_product_m1_u')
        UY = env.ref('kygl_website_membership.kygl_product_m1_y')
        #Supporting
        SM = env.ref('kygl_website_membership.kygl_product_m2_m')
        SU = env.ref('kygl_website_membership.kygl_product_m2_u')
        SY = env.ref('kygl_website_membership.kygl_product_m2_y')


        if type2 =="M" and type == 'A':
            product = UY
        if type2 =="M" and type == 'M':
            product = UM
        if type2 =="M" and type == 'U':
            product = UU

        if type2 =="H"  and type == 'A':
            product = HY
        if type2 =="H"  and type == 'M':
            product = HM
        if type2 =="H"  and type == 'U':
            product = HU

        if type2 =="S"  and type == 'A':
            product = SY
        if type2 =="S"  and type == 'M':
            product = SM
        if type2 =="S" and type == 'U':
            product = SU
        if type == 'A':
            day = 365
        if type == 'M':
            day = 31
        if type == 'U':
            day = 365

        if partner:
            format = "%Y-%m-%d"
            print(partner.name)
            print(date_start)
            datestart = datetime.datetime.strptime(date_start, format) if date_start != 'NULL' else datetime.datetime.today()
            print(datestart)
            datestop = (datetime.datetime.strptime(date_start, format) if date_start != 'NULL' else datetime.datetime.today()) + timedelta(days=day)
            datestopabo = datestop
            if type in ['A', 'M'] and datestopabo < datetime.datetime.today():
                datestopabo = '2021-%s' % str(datestopabo)[5:]
            if type in ['A','M'] and datestopabo < datetime.datetime.today():
                datestopabo = '2022-%s' % str(datestopabo)[5:]
            print(datestart)
            print(datestop)
            print(datestopabo)
            so = so_model.create({
                'partner_id': partner.id,
                'date_order': datestart,
                'company_id': 2,
                'order_line': [
                    (0, 0, {
                        'product_id': product.id,
                        'name': product.name,
                        'product_uom_qty':1,
                        'price_unit':  product.list_price,
                    }),
                ],
            })
            so.action_confirm()
            subscription = so.order_line[0].subscription_id
            move = move_model.create({
                'move_type': 'out_invoice',
                'partner_id': partner.id,
                'invoice_date': datestart,
                'journal_id': 1,
                'line_ids': [
                    (0, 0, {
                        'product_id': product.id,
                        'name': product.name,
                        'account_id': product.property_account_income_id.id or product.categ_id.property_account_income_categ_id.id,
                        'credit': product.list_price,
                        'debit': 0.0,
                    }),
                    (0, 0, {
                        'name': product.name,
                        'account_id': product.property_account_income_id.id or product.categ_id.property_account_income_categ_id.id,
                        'credit': 0.0,
                        'debit': product.list_price,
                    }),
                ],
            })
            move.action_post()
            member = membership_model.search([('account_invoice_id','=',move.id)])
            partner.write({'membership_start': datestart,
                           'membership_stop': datestopabo,
            })
            member.write({'date':datestart})
            subscription.write({'date_start':datestart,
                                'recurring_next_date':datestopabo})
        else:
            print('error',partref)

    i += 1
env.cr.commit()
print('Done %s' % i)

exit()
