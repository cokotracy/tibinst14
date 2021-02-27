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
{
    'name': "Website Booking KYGL",
    'category': 'tools',
    'version': '1.0.0',
    'description': """
    		Website Booking KYGL
        """,
    'currency': "EUR",
    'website':"www.olabs.be",
    'author': "O'labs",
    'depends': [
                'product',
                'website_sale',
                'calendar',
                'stock',
                'hr',
                'planning',
                'sale_subscription',
                'base_automation',
                'website_event_questions',
                'website_event_sale',
                'membership',
                'account_sign_up_details',
                ],
    'data': [
        "security/ir.model.access.csv",
        "data/res_company_data.xml",
        "data/ir_rule_data.xml",
        "data/planning_role_data.xml",
        "data/product_category_data.xml",
        "data/product_product_data.xml",
        "data/membership_data.xml",
        "data/uom_category_data.xml",
        "data/ir_sequence.xml",
        "data/cron_data.xml",
        "views/assets.xml",
        "views/answer.xml",
        "views/snippet.xml",
        'views/frontend.xml',
        "views/product.xml",
        "views/partner.xml",
        'views/sale.xml',
        'views/invoice.xml',
        'views/planning_slot_view.xml',
        'views/ir_config.xml',
        'views/reports.xml',
        'views/check.xml',
        'views/report_assets.xml',
        'views/event.xml',
        'report/layouts.xml',
        'views/menu.xml',
        'wizard/wizard_duplicate.xml',
         ],
    'images': ['static/description/banner.jpg'],
    'installable': True,
}
