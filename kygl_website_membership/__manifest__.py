# -*- coding: utf-8 -*-
# © 2020 Fabian Monoyer (Olabs Consulting SRL)
{
    'name': 'Membership Website',
    'summary': "Gestion Membership Website",
    'version': '12.0.1.0.1',
    'author': "Olabs Consulting ",
    'license': "AGPL-3",
    'maintainer': 'Olabs Consulting',
    'category': 'Extra Tools',
    'depends': ['base',
                'kygl_website_donation'],
    'data': [
        'data/product_product_data.xml',
        'views/page_membership_view.xml',
    ],
    'auto_install': False,
    'installable': True,
}
