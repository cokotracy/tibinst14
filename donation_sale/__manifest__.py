# -*- coding: utf-8 -*-
# © 2016 La Cimade (http://www.lacimade.org/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Donation Sale for KYGL',
    'version': '10.0.1.0.0',
    'category': 'Accounting & Finance',
    'license': 'AGPL-3',
    'summary': 'Manage donations in sale orders for KYGL',
    'author': "La Cimade, Akretion, Odoo Community Association (OCA),O'labs",
    'website': 'http://www.olabs.be',
    'depends': ['donation_base', 'sale','website_sale'],
    'data': [
        'views/account_invoice.xml',
        'views/sale_order.xml',
        'views/donation_tax.xml',
        'data/cron.xml',
        ],
    'installable': True,
}
