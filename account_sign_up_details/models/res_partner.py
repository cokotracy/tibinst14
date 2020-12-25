# -*- coding: utf-8 -*-
#################################################################################
#
#    Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#
#################################################################################
from odoo import api, fields, models, _

class ResPartner(models.Model):
	_inherit = 'res.partner'

	birtday = fields.Date('Date of Birth')
	gender = fields.Selection([('male', 'Male'),('female', 'Female'),('other', 'Other')])
