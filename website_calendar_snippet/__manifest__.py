# -*- coding: utf-8 -*-
# © 2016 ONESTEiN BV (<http://www.onestein.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Calendar Snippet',
    'images': [],
    'category': 'Website',
    'summary': 'Snippet for website',
    'version': '1.0.0',
    'author': "O'labs",
    'license': 'AGPL-3',
    'website': 'http://www.olabs.be',
    'depends': ['website', 'calendar', 'web'],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'templates/website_calendar_snippet.xml',
    ],
    'installable': True,
}
