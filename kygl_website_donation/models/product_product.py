# -*- coding: utf-8 -*-
# © 2020 Fabian Monoyer (Olabs Consulting SRL)

from odoo import models,fields,api, _


class KyglProduct(models.Model):
    """Adds Code Donation"""

    _inherit = 'product.template'

    kygl_code = fields.Char(string="Code Donation/Membership")
    kygl_info = fields.Html(string="Banner HTML", translate=True, sanitize=False)