# -*- coding: utf-8 -*-
#################################################################################
#
#    Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#
#################################################################################

import logging
from odoo.http import request
from odoo.addons.web.controllers.main import ensure_db, Home
from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class TibinstPortal(CustomerPortal):
	MANDATORY_BILLING_FIELDS = ["name", "phone", "email", "street", "city", "country_id"]
	OPTIONAL_BILLING_FIELDS = ["zipcode", "state_id", "vat", "company_name","lang"]

	_items_per_page = 20

class AuthSignupHome(Home):

	def do_signup(self, qcontext):
		""" Shared helper that creates a res.partner out of a token """
		values = { key: qcontext.get(key) for key in ('login', 'name', 'password', 'birthday','gender','lang') }
		if not values:
			raise UserError(_("The form was not properly filled in."))
		if values.get('password') != qcontext.get('confirm_password'):
			raise UserError(_("Passwords do not match; please retype them."))
		supported_langs = [lang['code'] for lang in request.env['res.lang'].sudo().search_read([], ['code'])]
		if request.lang in supported_langs:
			values['lang'] = request.lang
		self._signup_with_values(qcontext.get('token'), values)
		request.env.cr.commit()
