# -*- coding: utf-8 -*-
from odoo import fields, models
from datetime import date, timedelta
import logging
_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = 'account.move'

    def _post(self,soft=True):
        res = super(AccountMove,self)._post(soft)
        for record in self.filtered(lambda k: k.move_type == "out_invoice"):
            for line in record.invoice_line_ids:
                if line.product_id.membership:
                    day = 365 #default
                    if line.product_id.subscription_template_id:
                        day = 1
                        if line.product_id.subscription_template_id.recurring_rule_type == 'monthly':
                           day = 30
                        if line.product_id.subscription_template_id.recurring_rule_type == 'yearly':
                           day = 365
                        day = day * line.product_id.subscription_template_id.recurring_interval
                    membership_line = self.env['membership.membership_line'].search([("account_invoice_id","=",record.id)])
                    membership_line.write({"date_from":fields.Date.today() ,"date_to":fields.Date.today() + timedelta(days=day)})
        return res


