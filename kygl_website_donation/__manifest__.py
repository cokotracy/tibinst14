# -*- coding: utf-8 -*-
# © 2020 Fabian Monoyer (Olabs Consulting SRL)
{
    'name': 'Donation Website',
    'summary': "Gestion Donation Website",
    'version': '12.0.1.0.1',
    'author': "Olabs Consulting ",
    'license': "AGPL-3",
    'maintainer': 'Olabs Consulting',
    'category': 'Extra Tools',
    'depends': ['base',
                'donation_base',
                'donation_sale',
                'website_booking'],
    'data': [
        'data/ir_config_parameter_data.xml',
        'data/product_product_data.xml',
        'views/page_donation_view.xml',
        'views/product_product_view.xml',
        'views/sale_order_view.xml',
    ],
    'auto_install': False,
    'installable': True,
}
